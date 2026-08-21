#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""brand.py — Nguồn chân lý duy nhất cho hệ thống thiết kế (email + web)."""

import hashlib

BRAND_NAME = "BẢN TIN HẰNG NGÀY"
BRAND_TAGLINE = "Trợ lý tin tức của San"

# Đổi thành URL GitHub Pages thật sau khi deploy lần đầu
SITE_URL = "https://xuansan1970.github.io/bot-news-cloud/"

# ── Bảng màu Dark Premium ────────────────────────────────────────────────
INK = {
    "bg": "#080b14",
    "surface": "#11162a",
    "surface_2": "#1a2138",
    "border": "#252d47",
    "text": "#f1f5f9",
    "muted": "#94a3b8",
    "faint": "#64748b",
}

# Mỗi chuyên mục một cặp màu — dùng thống nhất cho accent bar, chip, gradient
CATEGORY_THEME = {
    "vn_hot":     {"accent": "#ff5470", "accent_2": "#ff8a5b", "emoji": "🔥", "short": "Tin nóng"},
    "vn_tech":    {"accent": "#22d3ee", "accent_2": "#4f8cff", "emoji": "💻", "short": "Công nghệ"},
    "vn_economy": {"accent": "#34d399", "accent_2": "#a3e635", "emoji": "📈", "short": "Kinh tế"},
    "vn_science": {"accent": "#c084fc", "accent_2": "#818cf8", "emoji": "🔬", "short": "Khoa học"},
    "vn_world":   {"accent": "#60a5fa", "accent_2": "#38bdf8", "emoji": "🌍", "short": "Thế giới"},
    "vn_weird":   {"accent": "#fbbf24", "accent_2": "#fb923c", "emoji": "🤩", "short": "Hay & Lạ"},
}

DEFAULT_THEME = {"accent": "#7c8cff", "accent_2": "#a78bfa", "emoji": "📰", "short": "Tin tức"}


def theme_for(cat_key: str) -> dict:
    return CATEGORY_THEME.get(cat_key, DEFAULT_THEME)


def placeholder_colors(seed: str) -> tuple:
    """Sinh cặp màu ổn định từ tên nguồn — cùng một nguồn luôn ra cùng màu.

    Dùng cho thẻ gradient thay ảnh, nên bản tin không bao giờ có ô ảnh vỡ.
    """
    h = int(hashlib.md5(seed.encode("utf-8")).hexdigest()[:8], 16)
    palettes = [
        ("#2b3a67", "#4a5fc1"), ("#3b2f63", "#6d4aa8"), ("#123a4d", "#1e6f8c"),
        ("#3d2438", "#8a4a6d"), ("#1f3d33", "#3d8a6b"), ("#42301c", "#a06a32"),
        ("#2a2f4a", "#5b6494"), ("#4a2731", "#a04a58"),
    ]
    return palettes[h % len(palettes)]


def initials(name: str) -> str:
    parts = [p for p in name.replace("-", " ").split() if p]
    if not parts:
        return "TT"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[1][0]).upper()
