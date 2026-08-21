#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
site_builder.py — Sinh website tĩnh cho GitHub Pages.

Cấu trúc thư mục xuất ra:
    docs/
      index.html              ← bản tin hôm nay
      d/YYYY-MM-DD.html       ← lưu trữ từng ngày (tự chứa, mở offline được)
      archive.json            ← danh sách ngày đã có
      manifest.webmanifest    ← để cài lên màn hình chính điện thoại
      sw.js                   ← service worker cho PWA
      icon.svg / icon.png
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from string import Template

from brand import BRAND_NAME, initials, placeholder_colors, theme_for
from site_template import PAGE

logger = logging.getLogger(__name__)

WEEKDAYS = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
KEEP_DAYS = 60          # giữ lại 60 bản lưu trữ gần nhất


def _now_vn() -> datetime:
    return datetime.utcnow() + timedelta(hours=7)


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower())[:40].strip("-")


def _rel_time(iso: str, now: datetime) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        mins = int((now.replace(tzinfo=dt.tzinfo) - dt).total_seconds() // 60)
        if mins < 60:
            return f"{max(mins, 1)} phút trước"
        if mins < 1440:
            return f"{mins // 60} giờ trước"
        return f"{mins // 1440} ngày trước"
    except Exception:
        return ""


def build_payload(news_data: dict) -> tuple:
    """Chuyển news_data thành JSON gọn cho trình duyệt + thống kê ảnh."""
    now = _now_vn()
    sections, idx, with_img, total = [], 0, 0, 0

    for cat_key, cat in news_data.items():
        th = theme_for(cat_key)
        arts = []
        for rank, a in enumerate(cat["articles"]):
            idx += 1
            total += 1
            has_img = bool(a.get("thumbnail")) and not a.get("thumb_fallback")
            if has_img:
                with_img += 1
            c1, c2 = placeholder_colors(a.get("source_name", "news"))
            arts.append({
                "id": f"{cat_key}-{idx}-{_slug(a['title'])}",
                "i": idx,
                "title": a["title"],
                "link": a["link"],
                "summary": a.get("summary", ""),
                "source": a.get("source_name", ""),
                "time": _rel_time(a.get("pub_date", ""), now),
                "thumbnail": a["thumbnail"] if has_img else None,
                "hot": cat_key == "vn_hot" and rank < 2,
                "ph": {"c1": c1, "c2": c2,
                       "ini": initials(a.get("source_name", "TT")),
                       "src": a.get("source_name", "")},
            })
        if arts:
            sections.append({
                "key": cat_key, "name": cat["name"], "short": th["short"],
                "emoji": th["emoji"], "accent": th["accent"], "articles": arts,
            })

    pct = (with_img * 100 // total) if total else 0
    return sections, total, pct


def _render_page(sections, weather, archive, total, pct, day: datetime, base: str) -> str:
    date_display = f"{WEEKDAYS[day.weekday()]}, {day.strftime('%d/%m/%Y')}"
    hero = "Sáng nay có gì đáng đọc?"
    return Template(PAGE).safe_substitute(
        TITLE=f"{BRAND_NAME} · {day.strftime('%d/%m/%Y')}",
        BRAND=BRAND_NAME,
        HERO_TITLE=hero,
        DATE_DISPLAY=date_display,
        DATE_ISO=day.strftime("%Y-%m-%d"),
        UPDATED=day.strftime("%H:%M %d/%m/%Y"),
        TOTAL=str(total),
        THUMB_PCT=str(pct),
        BASE=base,
        DATA_JSON=json.dumps(sections, ensure_ascii=False, separators=(",", ":")),
        WEATHER_JSON=json.dumps(weather or {"ok": False}, ensure_ascii=False),
        ARCHIVE_JSON=json.dumps(archive, ensure_ascii=False, separators=(",", ":")),
    )


MANIFEST = {
    "name": BRAND_NAME, "short_name": "Bản Tin", "start_url": "./index.html",
    "display": "standalone", "background_color": "#080b14", "theme_color": "#080b14",
    "description": "Bản tin tổng hợp mỗi sáng",
    "icons": [
        {"src": "./icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any"},
        {"src": "./icon.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
    ],
}

SW = """const C='bantin-v1';
self.addEventListener('install',e=>{self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>
  Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{
  const r=e.request; if(r.method!=='GET')return;
  const u=new URL(r.url); if(u.origin!==location.origin)return;
  e.respondWith(fetch(r).then(res=>{
    const copy=res.clone(); caches.open(C).then(c=>c.put(r,copy)); return res;
  }).catch(()=>caches.match(r)));
});"""

ICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#4f8cff"/><stop offset="1" stop-color="#a78bfa"/></linearGradient></defs>
<rect width="128" height="128" rx="28" fill="url(#g)"/>
<rect x="26" y="34" width="76" height="10" rx="5" fill="#fff" opacity=".95"/>
<rect x="26" y="54" width="58" height="8" rx="4" fill="#fff" opacity=".75"/>
<rect x="26" y="70" width="66" height="8" rx="4" fill="#fff" opacity=".6"/>
<rect x="26" y="86" width="42" height="8" rx="4" fill="#fff" opacity=".45"/>
</svg>"""



def _write_png_icon(path: Path, size: int = 512) -> None:
    """Icon PNG cho màn hình chính iOS/Android. Bỏ qua êm nếu thiếu Pillow."""
    if path.exists():
        return
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return
    img = Image.new("RGB", (size, size))
    d = ImageDraw.Draw(img)
    for y in range(size):                      # gradient chéo brand
        t = y / size
        d.line([(0, y), (size, y)],
               fill=(int(79 + (167 - 79) * t), int(140 + (139 - 140) * t), int(255 + (250 - 255) * t)))
    bars = [(0.20, 0.26, 0.80, 0.34, 245), (0.20, 0.42, 0.66, 0.48, 195),
            (0.20, 0.55, 0.72, 0.61, 160), (0.20, 0.68, 0.53, 0.74, 120)]
    for x0, y0, x1, y1, a in bars:
        d.rounded_rectangle([x0 * size, y0 * size, x1 * size, y1 * size],
                            radius=size * 0.02, fill=(255, 255, 255))
    img.save(path, "PNG", optimize=True)

def build_site(news_data: dict, weather: dict = None, out_dir: Path = None) -> dict:
    """Sinh toàn bộ website. Trả về thống kê để log/hiển thị."""
    out = Path(out_dir or (Path(__file__).parent / "docs"))
    (out / "d").mkdir(parents=True, exist_ok=True)

    day = _now_vn()
    date_iso = day.strftime("%Y-%m-%d")
    sections, total, pct = build_payload(news_data)

    # ── Cập nhật danh sách lưu trữ ──────────────────────────────────────
    arch_file = out / "archive.json"
    archive = []
    if arch_file.exists():
        try:
            archive = json.loads(arch_file.read_text("utf-8"))
        except Exception:
            archive = []
    archive = [a for a in archive if a.get("date") != date_iso]
    archive.insert(0, {
        "date": date_iso,
        "label": f"{WEEKDAYS[day.weekday()]}, {day.strftime('%d/%m/%Y')}",
        "total": total,
    })
    archive = archive[:KEEP_DAYS]
    arch_file.write_text(json.dumps(archive, ensure_ascii=False, indent=1), "utf-8")

    # ── Trang hôm nay + bản lưu trữ của chính ngày đó ──────────────────
    (out / "index.html").write_text(
        _render_page(sections, weather, archive, total, pct, day, "./"), "utf-8")
    (out / "d" / f"{date_iso}.html").write_text(
        _render_page(sections, weather, archive, total, pct, day, "../"), "utf-8")

    # ── Tài nguyên PWA ──────────────────────────────────────────────────
    (out / "manifest.webmanifest").write_text(
        json.dumps(MANIFEST, ensure_ascii=False, indent=1), "utf-8")
    (out / "sw.js").write_text(SW, "utf-8")
    (out / "icon.svg").write_text(ICON, "utf-8")
    _write_png_icon(out / "icon.png")
    (out / ".nojekyll").write_text("", "utf-8")

    # ── Dọn bản lưu trữ quá cũ ─────────────────────────────────────────
    keep = {a["date"] for a in archive}
    for f in (out / "d").glob("*.html"):
        if f.stem not in keep:
            f.unlink(missing_ok=True)

    logger.info(f"  🌐 Website: {total} tin · {pct}% có ảnh · {len(archive)} ngày lưu trữ")
    return {"total": total, "thumb_pct": pct, "days": len(archive), "out": str(out)}
