#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news_fetcher.py — Thu thập tin tức từ RSS feeds + kiểm tra link + lọc chất lượng
"""

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path

import socket

import feedparser
import requests
from dateutil import parser as dateutil_parser

from thumbnail_resolver import resolve_batch

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent
SOURCES_FILE = SCRIPT_DIR / "sources.json"
FEED_TIMEOUT = 12
socket.setdefaulttimeout(20)  # chốt chặn cuối, không thư viện nào được treo vô hạn
LINK_CHECK_TIMEOUT = 5
HOURS_BACK = 36

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8",
}


def load_sources() -> dict:
    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_date(entry) -> datetime:
    for field in ("published_parsed", "updated_parsed", "created_parsed"):
        val = getattr(entry, field, None)
        if val:
            try:
                return datetime(*val[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    for field in ("published", "updated", "created"):
        val = getattr(entry, field, None)
        if val:
            try:
                dt = dateutil_parser.parse(val)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except Exception:
                pass
    return datetime.now(timezone.utc)


def check_url_accessible(url: str) -> bool:
    """Kiểm tra link có vào được không."""
    try:
        resp = requests.head(url, timeout=LINK_CHECK_TIMEOUT,
                             allow_redirects=True, headers=HEADERS)
        if resp.status_code < 400:
            return True
        resp = requests.get(url, timeout=LINK_CHECK_TIMEOUT,
                            headers=HEADERS, stream=True)
        resp.close()
        return resp.status_code < 400
    except Exception:
        return False


def validate_links_parallel(articles: list, max_workers: int = 20) -> list:
    """Kiểm tra song song, chỉ giữ bài có link hợp lệ."""
    if not articles:
        return []
    logger.info(f"  🔍 Kiểm tra {len(articles)} link...")
    valid, failed = [], 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_url_accessible, art["link"]): art for art in articles}
        for future in as_completed(futures):
            art = futures[future]
            try:
                if future.result():
                    valid.append(art)
                else:
                    failed += 1
            except Exception:
                failed += 1
    valid.sort(key=lambda x: x["pub_date_dt"], reverse=True)
    logger.info(f"  ✅ {len(valid)} link OK / ❌ {failed} lỗi")
    return valid


def fetch_feed(source: dict) -> list:
    """Fetch một RSS feed."""
    import re
    url, name = source["url"], source["name"]
    try:
        resp = requests.get(url, headers=HEADERS, timeout=FEED_TIMEOUT)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
    except Exception as e:
        logger.warning(f"❌ {name}: bỏ qua ({str(e)[:60]})")
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS_BACK)
    items = []

    for entry in feed.entries:
        try:
            pub = parse_date(entry)
            if pub < cutoff:
                continue
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            if not title or not link:
                continue

            # Tóm tắt
            summary = ""
            for field in ("summary", "description", "content"):
                raw = entry.get(field, "")
                if isinstance(raw, list):
                    raw = raw[0].get("value", "") if raw else ""
                if raw:
                    summary = re.sub(r"<[^>]+>", " ", raw)
                    summary = re.sub(r"\s+", " ", summary).strip()
                    if len(summary) > 280:
                        summary = summary[:277] + "..."
                    break

            # Thumbnail
            thumb = None
            if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                thumb = entry.media_thumbnail[0].get("url")
            elif hasattr(entry, "media_content") and entry.media_content:
                for mc in entry.media_content:
                    if mc.get("medium") == "image" or mc.get("type", "").startswith("image"):
                        thumb = mc.get("url")
                        break
            elif entry.get("enclosures"):
                for enc in entry.enclosures:
                    if enc.get("type", "").startswith("image"):
                        thumb = enc.get("href")
                        break
            if not thumb:
                m = re.search(r'src=["\']([^"\']+\.(jpg|jpeg|png|webp))["\']',
                              entry.get("summary", ""), re.IGNORECASE)
                if m:
                    thumb = m.group(1)

            items.append({
                "title": title,
                "link": link,
                "summary": summary,
                "thumbnail": thumb,
                "source_name": name,
                "source_lang": source.get("lang", "vi"),
                "pub_date": pub.isoformat(),
                "pub_date_dt": pub,
            })
        except Exception:
            pass

    return items


def fetch_all_news() -> dict:
    """Thu thập, lọc chất lượng, kiểm tra link, trả về dict kết quả."""
    from content_filter import filter_and_rank

    data = load_sources()
    result = {}

    for cat_key, cat_info in data["categories"].items():
        cat_name = cat_info["name"]
        sources = cat_info["sources"]
        max_art = cat_info.get("max_articles", 8)
        layout = cat_info.get("layout", "list")
        accent = cat_info.get("accent", "#3b82f6")

        all_articles = []
        logger.info(f"\n📂 {cat_name} — {len(sources)} nguồn")

        for source in sources:
            articles = fetch_feed(source)
            logger.info(f"  ✅ {source['name']}: {len(articles)} bài")
            all_articles.extend(articles)
            time.sleep(0.15)

        # Dedup
        seen, deduped = set(), []
        for art in all_articles:
            key = art["title"][:55].lower().strip()
            if key not in seen:
                seen.add(key)
                deduped.append(art)

        # Lọc & chấm điểm chất lượng
        logger.info(f"  🎯 Đang chấm điểm {len(deduped)} bài...")
        ranked = filter_and_rank(deduped, min_score=-2.0)
        logger.info(f"  ✅ {len(ranked)} bài qua lọc chất lượng")

        # Lấy gấp 3 hoặc tối thiểu 20 bài để bù link lỗi
        candidates = ranked[: max(max_art * 4, 28)]

        # Kiểm tra link + giải ảnh thumbnail trong cùng một vòng request
        valid = resolve_batch(candidates, max_workers=16)
        valid.sort(key=lambda x: x["pub_date_dt"], reverse=True)
        # Ưu tiên bài có ảnh thật lên trước, nhưng không hy sinh độ mới
        valid.sort(key=lambda x: (x.get("thumb_fallback", True),))
        final = valid[:max_art]

        result[cat_key] = {
            "name": cat_name,
            "articles": final,
            "layout": layout,
            "accent": accent,
        }
        logger.info(f"  → {len(final)} tin tức chọn lọc\n")

    return result


if __name__ == "__main__":
    news = fetch_all_news()
    total = sum(len(v["articles"]) for v in news.values())
    print(f"\n✅ Tổng cộng {total} tin tức chất lượng")
