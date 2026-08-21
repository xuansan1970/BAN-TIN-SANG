#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mailer.py — Gửi email bản tin.

Ưu tiên đọc thông tin đăng nhập từ BIẾN MÔI TRƯỜNG (an toàn, dùng được với
GitHub Secrets), chỉ khi thiếu mới quay về email_config.json để tương thích
ngược với cách chạy cũ trên máy Mac.
"""

from __future__ import annotations

import json
import logging
import os
import smtplib
import ssl
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path

logger = logging.getLogger(__name__)
CONFIG_FILE = Path(__file__).parent / "email_config.json"


def load_credentials() -> dict:
    cfg = {}
    if CONFIG_FILE.exists():
        try:
            cfg = json.loads(CONFIG_FILE.read_text("utf-8"))
        except Exception:
            cfg = {}
    sender = os.getenv("GMAIL_ADDRESS", "").strip() or cfg.get("sender_email", "")
    password = os.getenv("GMAIL_PASSWORD", "").strip() or cfg.get("sender_password", "")
    recipient = os.getenv("NEWS_RECIPIENT", "").strip() or cfg.get("recipient_email", "") or sender
    return {
        "sender": sender,
        "password": password.replace(" ", ""),
        "recipients": [r.strip() for r in recipient.split(",") if r.strip()],
        "host": cfg.get("smtp_host", "smtp.gmail.com"),
        "port": int(cfg.get("smtp_port", 587)),
    }


def send_news_email(html: str, total: int, site_url: str = "") -> bool:
    c = load_credentials()
    if not (c["sender"] and c["password"] and c["recipients"]):
        logger.error("❌ Thiếu GMAIL_ADDRESS / GMAIL_PASSWORD — không gửi được email.")
        return False

    vn = datetime.now(timezone(timedelta(hours=7)))
    weekdays = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
    subject = f"[{weekdays[vn.weekday()]}, {vn.strftime('%d/%m/%Y')}] Bản Tin Hằng Ngày — {total} tin mới"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = formataddr(("Trợ lý của San 📰", c["sender"]))
    msg["To"] = ", ".join(c["recipients"])

    plain = f"Bản tin hằng ngày — {total} tin mới.\nXem bản đầy đủ: {site_url}"
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(c["host"], c["port"], timeout=45) as s:
            s.ehlo()
            s.starttls(context=ctx)
            s.login(c["sender"], c["password"])
            s.sendmail(c["sender"], c["recipients"], msg.as_string())
        logger.info(f"  ✉️  Đã gửi tới {', '.join(c['recipients'])}")
        return True
    except Exception as e:
        logger.error(f"❌ Lỗi gửi email: {e}")
        return False
