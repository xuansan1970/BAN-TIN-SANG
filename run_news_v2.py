#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_news_v2.py — Điều phối toàn bộ bản tin buổi sáng.

    1. Thu thập tin từ sources.json
    2. Giải ảnh thumbnail + kiểm tra link (một vòng request duy nhất)
    3. Dựng email Dark Premium và gửi đi
    4. Sinh website tĩnh vào docs/ cho GitHub Pages

Chạy được cả trên máy Mac lẫn trong GitHub Actions, không cần sửa gì.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-email", action="store_true", help="chỉ dựng website, không gửi mail")
    ap.add_argument("--no-site", action="store_true", help="chỉ gửi mail, không dựng website")
    ap.add_argument("--limit", type=int, default=0, help="giới hạn số nguồn mỗi mục (để test nhanh)")
    args = ap.parse_args()

    from brand import SITE_URL
    from news_fetcher import fetch_all_news
    from render_email import render_email

    weather = None
    try:
        from weather_fetch import fetch_weather
        weather = fetch_weather()
    except Exception as e:
        logger.warning(f"⚠️  Không lấy được thời tiết: {e}")

    if args.limit:
        import json as _json
        import news_fetcher
        data = _json.load(open(Path(__file__).parent / "sources.json", encoding="utf-8"))
        for cat in data["categories"].values():
            cat["sources"] = cat["sources"][: args.limit]
        news_fetcher.load_sources = lambda: data

    logger.info("🔍 Thu thập tin tức...")
    news = fetch_all_news()
    total = sum(len(c["articles"]) for c in news.values())
    if total == 0:
        logger.error("❌ Không thu được tin nào — dừng lại, không ghi đè bản cũ.")
        return 1

    with_img = sum(1 for c in news.values() for a in c["articles"] if not a.get("thumb_fallback"))
    logger.info(f"📊 {total} tin · {with_img} có ảnh thật ({with_img * 100 // total}%)")

    if not args.no_site:
        from site_builder import build_site
        build_site(news, weather)

    html = render_email(news, weather, site_url=SITE_URL)
    Path(__file__).parent.joinpath("last_email.html").write_text(html, encoding="utf-8")

    if not args.no_email:
        from mailer import send_news_email
        send_news_email(html, total, SITE_URL)
    else:
        logger.info("  ✉️  Bỏ qua gửi mail (--no-email). Bản xem trước: last_email.html")

    logger.info("✅ Hoàn tất.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
