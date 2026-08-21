#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
thumbnail_resolver.py — Giải quyết triệt để tình trạng tin không có thumbnail.

Chuỗi 5 lớp, dừng ở lớp đầu tiên cho ra ảnh hợp lệ:
    1. Metadata RSS (media:thumbnail / media:content / enclosure)
    2. og:image  (+ og:image:secure_url)
    3. twitter:image (+ twitter:image:src)
    4. JSON-LD  "image"  /  itemprop="image"  /  link rel="image_src"
    5. Ảnh <img> lớn nhất nằm trong thân bài

Sau đó VALIDATE ảnh thật sự tải được và đủ lớn. Nếu tất cả đều trượt,
article được gắn cờ `thumb_fallback` để tầng render vẽ một thẻ gradient
có thương hiệu — KHÔNG BAO GIỜ để lại ô ảnh vỡ.
"""

from __future__ import annotations

import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse

import requests

logger = logging.getLogger(__name__)

PAGE_TIMEOUT = 10
LINK_TIMEOUT = 7
IMG_TIMEOUT = 6
MAX_PAGE_BYTES = 250_000          # chỉ cần phần <head>, không tải cả trang
MIN_IMAGE_BYTES = 6_000           # nhỏ hơn thường là icon/tracking pixel

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# URL chứa các mảnh này gần như chắc chắn không phải ảnh minh hoạ bài viết
JUNK_PATTERNS = re.compile(
    r"(logo|favicon|sprite|avatar|placeholder|default[-_.]|blank|"
    r"1x1|pixel|spacer|tracking|banner[-_]ad|adsystem|doubleclick|"
    r"share[-_]?fb|facebook\.com/tr)",
    re.IGNORECASE,
)

# Bắt kích thước nhúng trong tên file: foo_120x90.jpg
DIM_IN_NAME = re.compile(r"[_\-/](\d{2,4})x(\d{2,4})[_\-.]", re.IGNORECASE)

META_PATTERNS = [
    # (thứ tự ưu tiên, regex)
    re.compile(r'<meta[^>]+property=["\']og:image:secure_url["\'][^>]+content=["\']([^"\']+)', re.I),
    re.compile(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', re.I),
    re.compile(r'<meta[^>]+name=["\']twitter:image(?::src)?["\'][^>]+content=["\']([^"\']+)', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']twitter:image', re.I),
    re.compile(r'<meta[^>]+itemprop=["\']image["\'][^>]+content=["\']([^"\']+)', re.I),
    re.compile(r'<link[^>]+rel=["\']image_src["\'][^>]+href=["\']([^"\']+)', re.I),
]

JSONLD_IMAGE = re.compile(
    r'"image"\s*:\s*(?:\{[^{}]*?"url"\s*:\s*"([^"]+)"|"([^"]+)"|\[\s*"([^"]+)")',
    re.IGNORECASE | re.DOTALL,
)

IMG_TAG = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
IMG_SRC = re.compile(r'(?:data-)?src(?:et)?=["\']([^"\']+)', re.IGNORECASE)
IMG_W = re.compile(r'width=["\']?(\d+)', re.IGNORECASE)
IMG_H = re.compile(r'height=["\']?(\d+)', re.IGNORECASE)


def _looks_junk(url: str) -> bool:
    if not url or len(url) < 12:
        return True
    if JUNK_PATTERNS.search(url):
        return True
    m = DIM_IN_NAME.search(url)
    if m and (int(m.group(1)) < 200 or int(m.group(2)) < 120):
        return True
    return False


def _clean(url: str, base: str) -> str | None:
    """Chuẩn hoá URL ảnh: bỏ escape, ghép URL tương đối, ép https."""
    if not url:
        return None
    url = url.strip().replace("&amp;", "&").replace("\\/", "/").strip('"\' ')
    if url.startswith("//"):
        url = "https:" + url
    elif url.startswith("/"):
        url = urljoin(base, url)
    elif not url.startswith("http"):
        return None
    if url.startswith("http://"):
        url = "https://" + url[7:]
    return url if not _looks_junk(url) else None


def _biggest_inline_image(html: str, base: str) -> str | None:
    """Lớp 5: quét mọi <img>, chọn ảnh khai báo kích thước lớn nhất."""
    best, best_area = None, 0
    for tag in IMG_TAG.findall(html)[:60]:
        m = IMG_SRC.search(tag)
        if not m:
            continue
        src = _clean(m.group(1).split()[0], base)
        if not src:
            continue
        w = IMG_W.search(tag)
        h = IMG_H.search(tag)
        area = (int(w.group(1)) if w else 0) * (int(h.group(1)) if h else 0)
        if area == 0:
            area = 1  # không khai báo size — vẫn giữ làm ứng viên cuối
        if area > best_area:
            best, best_area = src, area
    return best


def extract_from_page(url: str) -> tuple[bool, str | None]:
    """Tải phần đầu trang bài viết. Trả về (link_sống, url_ảnh_ứng_viên).

    Gộp luôn việc kiểm tra link còn sống — tiết kiệm một vòng request so với
    code cũ (vốn gọi HEAD riêng rồi GET riêng).
    """
    try:
        resp = requests.get(
            url, headers=HEADERS, timeout=PAGE_TIMEOUT, stream=True, allow_redirects=True
        )
        if resp.status_code >= 400:
            resp.close()
            return False, None

        chunks, size = [], 0
        for chunk in resp.iter_content(16_384):
            chunks.append(chunk)
            size += len(chunk)
            if size >= MAX_PAGE_BYTES:
                break
        resp.close()
        html = b"".join(chunks).decode(resp.encoding or "utf-8", errors="ignore")
        base = f"{urlparse(resp.url).scheme}://{urlparse(resp.url).netloc}"

        # Lớp 2-4: các thẻ meta
        for pattern in META_PATTERNS:
            m = pattern.search(html)
            if m:
                candidate = _clean(m.group(1), base)
                if candidate:
                    return True, candidate

        # Lớp 4b: JSON-LD
        m = JSONLD_IMAGE.search(html)
        if m:
            raw = m.group(1) or m.group(2) or m.group(3)
            candidate = _clean(raw, base)
            if candidate:
                return True, candidate

        # Lớp 5: ảnh lớn nhất trong thân bài
        return True, _biggest_inline_image(html, base)

    except Exception:
        return False, None


def image_is_real(url: str) -> bool:
    """Xác nhận URL trả về đúng một file ảnh và đủ nặng để không phải icon."""
    if not url:
        return False
    try:
        resp = requests.head(url, headers=HEADERS, timeout=IMG_TIMEOUT, allow_redirects=True)
        if resp.status_code >= 400 or "image" not in resp.headers.get("Content-Type", ""):
            # Một số CDN chặn HEAD — thử GET 1 phần nhỏ
            resp = requests.get(
                url, headers={**HEADERS, "Range": "bytes=0-2048"},
                timeout=IMG_TIMEOUT, stream=True, allow_redirects=True
            )
            ctype = resp.headers.get("Content-Type", "")
            ok = resp.status_code < 400 and "image" in ctype
            resp.close()
            return ok
        length = resp.headers.get("Content-Length")
        if length and int(length) < MIN_IMAGE_BYTES:
            return False
        return True
    except Exception:
        return False


def link_alive(url: str) -> bool:
    """Kiểm tra link còn sống bằng cách rẻ nhất.

    Nhiều báo chặn bot bằng 403/405 nhưng link vẫn mở bình thường trên trình
    duyệt — coi các mã đó là SỐNG, chỉ loại khi thật sự 404/410 hoặc không
    kết nối được. Nguyên tắc: thà giữ nhầm còn hơn bỏ sót tin.
    """
    try:
        r = requests.head(url, headers=HEADERS, timeout=LINK_TIMEOUT, allow_redirects=True)
        if r.status_code < 400 or r.status_code in (403, 405, 429, 999):
            return True
        if r.status_code in (404, 410):
            return False
    except requests.Timeout:
        return True          # chậm không có nghĩa là chết
    except Exception:
        pass
    try:
        r = requests.get(url, headers=HEADERS, timeout=LINK_TIMEOUT,
                         stream=True, allow_redirects=True)
        code = r.status_code
        r.close()
        return code < 400 or code in (403, 405, 429, 999)
    except requests.Timeout:
        return True
    except Exception:
        return False


def _good_rss_thumb(art: dict) -> str | None:
    t = art.get("thumbnail")
    if not t:
        return None
    t = _clean(t, art.get("link", ""))
    return t


def resolve_batch(articles: list, max_workers: int = 14) -> list:
    """Kiểm tra link + bảo đảm mỗi bài có ảnh minh hoạ.

    Chỉ tải trang bài viết khi RSS KHÔNG kèm ảnh — nhờ vậy giảm mạnh số
    request nặng, tránh bị các báo chặn vì gọi dồn dập, và giữ lại được
    nhiều tin hơn.

    Mỗi bài trả về được bổ sung:
        thumbnail      — URL ảnh đã xác thực, hoặc None
        thumb_fallback — True nếu tầng render phải vẽ thẻ gradient thay ảnh
    """
    if not articles:
        return []

    with_thumb, without_thumb = [], []
    for art in articles:
        cand = _good_rss_thumb(art)
        art["_cand"] = cand
        (with_thumb if cand else without_thumb).append(art)

    logger.info(
        f"  🖼  {len(articles)} bài · {len(with_thumb)} có ảnh sẵn từ RSS · "
        f"{len(without_thumb)} cần dò ảnh trong trang"
    )

    alive: list = []

    # Nhánh 1 — đã có ảnh: chỉ cần xác nhận link còn sống (rẻ)
    if with_thumb:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futs = {pool.submit(link_alive, a["link"]): a for a in with_thumb}
            for f in as_completed(futs):
                if _safe(f):
                    alive.append(futs[f])

    # Nhánh 2 — thiếu ảnh: tải trang, vừa xác nhận link vừa tìm ảnh
    if without_thumb:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futs = {pool.submit(extract_from_page, a["link"]): a for a in without_thumb}
            for f in as_completed(futs):
                art = futs[f]
                try:
                    ok, found = f.result()
                except Exception:
                    ok, found = False, None
                if not ok:
                    # Trang chặn bot vẫn có thể mở được với người đọc
                    if not link_alive(art["link"]):
                        continue
                art["_cand"] = found
                alive.append(art)

    # Xác thực ảnh — song song, gộp trùng URL
    jobs: dict = {}
    for art in alive:
        c = art.pop("_cand", None)
        if c:
            jobs.setdefault(c, []).append(art)

    good = set()
    if jobs:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futs = {pool.submit(image_is_real, u): u for u in jobs}
            for f in as_completed(futs):
                if _safe(f):
                    good.add(futs[f])

    for art in alive:
        art["thumbnail"] = None
        art["thumb_fallback"] = True
    for url, owners in jobs.items():
        if url in good:
            for art in owners:
                art["thumbnail"] = url
                art["thumb_fallback"] = False

    have = sum(1 for a in alive if not a["thumb_fallback"])
    if alive:
        logger.info(
            f"  ✅ {len(alive)}/{len(articles)} link sống · {have} có ảnh thật "
            f"({have * 100 // len(alive)}%) · {len(alive) - have} dùng thẻ thương hiệu"
        )
    return alive


def _safe(fut) -> bool:
    try:
        return bool(fut.result())
    except Exception:
        return False
