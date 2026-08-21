#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_email.py — Bản tin email Dark Premium.

Nguyên tắc kỹ thuật: toàn bộ layout dựng bằng <table> và style inline, không
dùng flex/grid/JS — đó là cách duy nhất hiển thị ổn định trên Gmail, Apple Mail
và Outlook. Khi một bài không có ảnh, ô ảnh được thay bằng thẻ gradient có mã
màu sinh từ tên nguồn, nên không bao giờ xuất hiện icon ảnh vỡ.
"""

from __future__ import annotations

import html as _html
from datetime import datetime, timedelta

from brand import (BRAND_NAME, BRAND_TAGLINE, INK, SITE_URL, initials,
                   placeholder_colors, theme_for)

WEEKDAYS = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',Arial,sans-serif"


def esc(t) -> str:
    return _html.escape(str(t or ""), quote=True)


def _now_vn() -> datetime:
    return datetime.utcnow() + timedelta(hours=7)


def _clamp(text: str, n: int) -> str:
    text = (text or "").strip()
    return text if len(text) <= n else text[: n - 1].rsplit(" ", 1)[0] + "…"


# ── Ô ảnh: ảnh thật hoặc thẻ gradient thương hiệu ────────────────────────
def _thumb(art: dict, w: int, h: int, radius: int = 10) -> str:
    src = art.get("thumbnail")
    if src and not art.get("thumb_fallback"):
        return (
            f'<img src="{esc(src)}" width="{w}" height="{h}" alt="" '
            f'style="display:block;width:{w}px;height:{h}px;object-fit:cover;'
            f'border-radius:{radius}px;border:0;outline:0;text-decoration:none;'
            f'background:{INK["surface_2"]};" />'
        )
    c1, c2 = placeholder_colors(art.get("source_name", "news"))
    return (
        f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" '
        f'width="{w}" style="width:{w}px;height:{h}px;border-radius:{radius}px;'
        f'background:{c2};background-image:linear-gradient(135deg,{c1} 0%,{c2} 100%);">'
        f'<tr><td align="center" valign="middle" style="height:{h}px;text-align:center;">'
        f'<div style="font:700 {max(13, h // 5)}px/1.1 {FONT};color:rgba(255,255,255,.92);'
        f'letter-spacing:1px;">{esc(initials(art.get("source_name", "TT")))}</div>'
        f'<div style="font:600 10px/1.4 {FONT};color:rgba(255,255,255,.6);'
        f'margin-top:3px;">{esc(_clamp(art.get("source_name", ""), 18))}</div>'
        f"</td></tr></table>"
    )


# ── Header ───────────────────────────────────────────────────────────────
def _header(total: int, weather: dict) -> str:
    vn = _now_vn()
    date_line = f"{WEEKDAYS[vn.weekday()]}, {vn.strftime('%d/%m/%Y')}"

    w_html = ""
    if weather and weather.get("ok"):
        temp = weather.get("temp", "—")
        city = weather.get("city", "TP. Hồ Chí Minh")
        desc = weather.get("desc", "")
        feels = weather.get("feels_like", temp)
        rain = weather.get("rain_prob", 0)
        tips = weather.get("tips") or weather.get("advice") or []
        tip_rows = "".join(
            f'<tr><td style="padding:3px 0;font:400 13px/1.5 {FONT};'
            f'color:{INK["muted"]};">{esc(t)}</td></tr>'
            for t in tips[:3]
        )
        w_html = f"""
        <tr><td style="padding:0 28px 22px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                 style="background:{INK['surface_2']};border:1px solid {INK['border']};border-radius:14px;">
            <tr><td style="padding:18px 20px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td style="font:700 19px/1.2 {FONT};color:{INK['text']};">{esc(city)}</td>
                  <td align="right" style="font:800 30px/1 {FONT};color:#7dd3fc;">{esc(temp)}°</td>
                </tr>
                <tr><td colspan="2" style="padding-top:5px;font:400 13px/1.5 {FONT};color:{INK['faint']};">
                  {esc(desc)} · Cảm giác {esc(feels)}° · Mưa {esc(rain)}%
                </td></tr>
              </table>
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                     style="margin-top:12px;border-top:1px solid {INK['border']};">
                <tr><td style="height:12px;"></td></tr>
                {tip_rows}
              </table>
            </td></tr>
          </table>
        </td></tr>"""

    return f"""
    <tr><td style="padding:0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
        <tr><td height="5" style="height:5px;font-size:0;line-height:0;
              background:#ff5470;background-image:linear-gradient(90deg,#ff5470,#fbbf24,#34d399,#22d3ee,#a78bfa);">&nbsp;</td></tr>
        <tr><td align="center" style="padding:34px 28px 6px;">
          <div style="font:800 27px/1.15 {FONT};color:{INK['text']};letter-spacing:-.4px;">{esc(BRAND_NAME)}</div>
          <div style="margin-top:8px;font:500 13px/1.4 {FONT};color:{INK['faint']};letter-spacing:.3px;">
            {esc(date_line)} · {esc(BRAND_TAGLINE)}
          </div>
        </td></tr>
        <tr><td align="center" style="padding:16px 28px 20px;">
          <table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
            <td style="padding:0 4px;"><span style="display:inline-block;padding:7px 13px;border-radius:99px;
                background:{INK['surface_2']};border:1px solid {INK['border']};
                font:600 12px/1 {FONT};color:#7dd3fc;">📊 {total} tin chọn lọc</span></td>
            <td style="padding:0 4px;"><span style="display:inline-block;padding:7px 13px;border-radius:99px;
                background:{INK['surface_2']};border:1px solid {INK['border']};
                font:600 12px/1 {FONT};color:#34d399;">✅ Link đã kiểm tra</span></td>
            <td style="padding:0 4px;"><span style="display:inline-block;padding:7px 13px;border-radius:99px;
                background:{INK['surface_2']};border:1px solid {INK['border']};
                font:600 12px/1 {FONT};color:#fbbf24;">🇻🇳 Ưu tiên Việt Nam</span></td>
          </tr></table>
        </td></tr>
        {w_html}
      </table>
    </td></tr>"""


# ── CTA sang website ─────────────────────────────────────────────────────
def _cta(site_url: str) -> str:
    return f"""
    <tr><td align="center" style="padding:4px 28px 30px;">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0">
        <tr><td align="center" bgcolor="#4f8cff" style="border-radius:99px;
            background:#4f8cff;background-image:linear-gradient(135deg,#4f8cff,#a78bfa);">
          <a href="{esc(site_url)}" target="_blank"
             style="display:inline-block;padding:14px 30px;font:700 15px/1 {FONT};
                    color:#ffffff;text-decoration:none;border-radius:99px;">
            📰 Mở trang đọc tin đầy đủ
          </a>
        </td></tr>
      </table>
      <div style="margin-top:10px;font:400 12px/1.5 {FONT};color:{INK['faint']};">
        Tìm kiếm · Lọc chủ đề · Lưu tin · Nghe đọc · Xem lại các ngày trước
      </div>
    </td></tr>"""


# ── Điểm tin 60 giây ─────────────────────────────────────────────────────
def _digest(news_data: dict, limit: int = 6) -> str:
    pool = []
    for cat_key, cat in news_data.items():
        th = theme_for(cat_key)
        for rank, art in enumerate(cat["articles"][:3]):
            pool.append((rank, cat_key, th, art))
    pool.sort(key=lambda x: x[0])
    picks = pool[:limit]
    if not picks:
        return ""

    rows = []
    for i, (_, _ck, th, art) in enumerate(picks, 1):
        rows.append(f"""
        <tr><td style="padding:11px 0;{'border-top:1px solid ' + INK['border'] + ';' if i > 1 else ''}">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
            <td width="30" valign="top" style="width:30px;">
              <div style="width:22px;height:22px;border-radius:6px;background:{th['accent']};
                   font:800 12px/22px {FONT};color:#07101f;text-align:center;">{i}</div>
            </td>
            <td valign="top">
              <a href="{esc(art['link'])}" target="_blank"
                 style="font:600 14.5px/1.45 {FONT};color:{INK['text']};text-decoration:none;">
                {esc(_clamp(art['title'], 110))}</a>
              <div style="margin-top:4px;font:500 11.5px/1.4 {FONT};color:{th['accent']};">
                {th['emoji']} {esc(art.get('source_name',''))}</div>
            </td>
          </tr></table>
        </td></tr>""")

    return f"""
    <tr><td style="padding:0 28px 26px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
             style="background:{INK['surface']};border:1px solid {INK['border']};border-radius:16px;">
        <tr><td style="padding:20px 22px 6px;">
          <div style="font:800 15px/1.2 {FONT};color:{INK['text']};letter-spacing:.4px;">
            ⚡ ĐIỂM TIN 60 GIÂY</div>
          <div style="margin-top:5px;font:400 12.5px/1.5 {FONT};color:{INK['faint']};">
            Bận thì đọc đúng phần này là đủ nắm ngày hôm nay</div>
        </td></tr>
        <tr><td style="padding:6px 22px 18px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">{''.join(rows)}</table>
        </td></tr>
      </table>
    </td></tr>"""


# ── Tiêu đề chuyên mục ───────────────────────────────────────────────────
def _section_head(name: str, th: dict, count: int) -> str:
    return f"""
    <tr><td style="padding:8px 28px 14px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
        <td width="4" style="width:4px;background:{th['accent']};border-radius:99px;">&nbsp;</td>
        <td style="padding-left:12px;font:800 17px/1.3 {FONT};color:{INK['text']};">{esc(name)}</td>
        <td align="right" style="font:600 11.5px/1 {FONT};color:{th['accent']};">{count} tin</td>
      </tr></table>
    </td></tr>"""


# ── Bố cục danh sách ─────────────────────────────────────────────────────
def _list_layout(articles: list, th: dict) -> str:
    rows = []
    for art in articles:
        rows.append(f"""
        <tr><td style="padding:0 28px 12px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                 style="background:{INK['surface']};border:1px solid {INK['border']};border-radius:14px;">
            <tr>
              <td width="128" valign="top" style="width:128px;padding:12px 0 12px 12px;">
                {_thumb(art, 116, 78)}
              </td>
              <td valign="top" style="padding:13px 14px 13px 12px;">
                <a href="{esc(art['link'])}" target="_blank"
                   style="font:600 14.5px/1.45 {FONT};color:{INK['text']};text-decoration:none;">
                  {esc(_clamp(art['title'], 105))}</a>
                <div style="margin-top:6px;font:400 12.5px/1.55 {FONT};color:{INK['muted']};">
                  {esc(_clamp(art.get('summary',''), 120))}</div>
                <div style="margin-top:8px;font:600 11px/1 {FONT};color:{th['accent']};">
                  {esc(art.get('source_name',''))}</div>
              </td>
            </tr>
          </table>
        </td></tr>""")
    return "".join(rows)


# ── Bố cục lưới 2 cột ────────────────────────────────────────────────────
def _grid_layout(articles: list, th: dict) -> str:
    cells = []
    for art in articles:
        cells.append(f"""
        <td width="50%" valign="top" style="width:50%;padding:0 5px 12px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                 style="background:{INK['surface']};border:1px solid {INK['border']};border-radius:14px;">
            <tr><td style="padding:10px 10px 0;">{_thumb(art, 244, 132)}</td></tr>
            <tr><td style="padding:11px 13px 14px;">
              <a href="{esc(art['link'])}" target="_blank"
                 style="font:600 14px/1.45 {FONT};color:{INK['text']};text-decoration:none;">
                {esc(_clamp(art['title'], 85))}</a>
              <div style="margin-top:7px;font:600 11px/1 {FONT};color:{th['accent']};">
                {esc(art.get('source_name',''))}</div>
            </td></tr>
          </table>
        </td>""")

    rows, i = [], 0
    while i < len(cells):
        pair = cells[i:i + 2]
        if len(pair) == 1:
            pair.append('<td width="50%" style="width:50%;">&nbsp;</td>')
        rows.append(f'<tr>{"".join(pair)}</tr>')
        i += 2

    return f"""
    <tr><td style="padding:0 23px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
        {''.join(rows)}
      </table>
    </td></tr>"""


def _footer(site_url: str) -> str:
    vn = _now_vn()
    return f"""
    <tr><td style="padding:22px 28px 34px;border-top:1px solid {INK['border']};">
      <div style="font:600 12.5px/1.6 {FONT};color:{INK['muted']};text-align:center;">
        {esc(BRAND_NAME)} · {esc(vn.strftime('%d/%m/%Y %H:%M'))}
      </div>
      <div style="margin-top:7px;font:400 11.5px/1.6 {FONT};color:{INK['faint']};text-align:center;">
        Tự động tổng hợp từ hơn 40 nguồn báo chính thống · Mọi liên kết đã được kiểm tra trước khi gửi
      </div>
      <div style="margin-top:12px;text-align:center;">
        <a href="{esc(site_url)}" target="_blank"
           style="font:600 12px/1 {FONT};color:#7dd3fc;text-decoration:none;">Mở website ↗</a>
      </div>
    </td></tr>"""


# ── Hàm chính ────────────────────────────────────────────────────────────
def render_email(news_data: dict, weather_data: dict = None,
                 daily_summary: dict = None, site_url: str = SITE_URL) -> str:
    total = sum(len(c["articles"]) for c in news_data.values())
    body = [_header(total, weather_data), _digest(news_data), _cta(site_url)]

    for cat_key, cat in news_data.items():
        arts = cat["articles"]
        if not arts:
            continue
        th = theme_for(cat_key)
        body.append(_section_head(cat["name"], th, len(arts)))
        if cat.get("layout") == "grid":
            body.append(_grid_layout(arts, th))
        else:
            body.append(_list_layout(arts, th))

    body.append(_footer(site_url))
    vn = _now_vn()

    return f"""<!DOCTYPE html>
<html lang="vi"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark">
<title>{esc(BRAND_NAME)} · {vn.strftime('%d/%m')}</title>
</head>
<body style="margin:0;padding:0;background:{INK['bg']};">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">
{esc(total)} tin chọn lọc sáng nay · Điểm tin 60 giây ở ngay đầu thư
</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
       bgcolor="{INK['bg']}" style="background:{INK['bg']};">
  <tr><td align="center" style="padding:16px 8px;">
    <table role="presentation" width="640" cellpadding="0" cellspacing="0" border="0"
           style="width:640px;max-width:100%;background:{INK['bg']};
                  border:1px solid {INK['border']};border-radius:20px;overflow:hidden;">
      {''.join(body)}
    </table>
  </td></tr>
</table>
</body></html>"""
