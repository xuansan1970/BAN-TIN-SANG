#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
content_filter.py — Chấm điểm & lọc chất lượng bài báo
Dựa trên hành vi đọc báo: GenK, Tinh Tế, Kinh tế, Khoa học, Công nghệ, Điều hay lạ
"""

# ─── Từ khóa GIẢM ĐIỂM (tin rác, clickbait, giải trí vô bổ) ───────────────
NEGATIVE_KEYWORDS = [
    # Showbiz / Giải trí vô bổ
    "hot girl", "sao việt", "lộ hàng", "gây sốt mạng xã hội",
    "diễn viên", "ca sĩ", "hoa hậu", "người mẫu", "idol kpop",
    "tình trường", "hẹn hò", "chia tay", "ly hôn của sao",
    "mv mới", "album mới", "liveshow",
    # Clickbait / Tiêu đề rẻ tiền
    "choáng váng khi", "sốc với", "không thể tin", "đừng bỏ lỡ",
    "ai cũng phải", "dân mạng tranh cãi", "gây bão",
    # Thương mại / Quảng cáo
    "khuyến mãi", "sale off", "giảm giá sốc", "flash sale", "ưu đãi độc quyền",
    "đặt hàng ngay", "mua ngay hôm nay",
    # Thể thao (kết quả thi đấu thuần túy)
    "bàn thắng", "tỷ số trận", "vô địch giải", "cúp quốc gia vô địch",
    # Làm đẹp / Giảm cân
    "thẩm mỹ viện", "giảm cân nhanh", "làm đẹp da", "collagen",
]

# ─── Từ khóa TĂNG ĐIỂM (tin chất lượng theo sở thích) ───────────────────────
POSITIVE_KEYWORDS = {
    # === CÔNG NGHỆ (ưu tiên cao — GenK & Tinh Tế style) ===
    "trí tuệ nhân tạo": 4, "ai ": 3, "chatgpt": 4, "gemini": 3,
    "openai": 4, "llm": 3, "model ai": 3, "deep learning": 3,
    "robot": 3, "chip": 3, "bán dẫn": 4, "nvidia": 3, "arm": 2,
    "iphone": 3, "apple": 2, "samsung": 2, "android": 2,
    "smartphone": 2, "laptop": 2, "màn hình": 1, "camera": 1,
    "phần mềm": 2, "ứng dụng": 1, "hệ điều hành": 2,
    "blockchain": 3, "tiền mã hóa": 2, "bitcoin": 2, "web3": 2,
    "metaverse": 2, "ar": 1, "vr": 1, "5g": 2, "6g": 3,
    "xe điện": 3, "tesla": 2, "tự lái": 3, "autopilot": 2,
    "google": 2, "meta": 2, "microsoft": 2, "amazon": 1,
    "công nghệ": 2, "số hóa": 2, "chuyển đổi số": 2,
    "hack": 2, "bảo mật": 2, "an ninh mạng": 3, "mã độc": 2,
    "lỗ hổng": 2, "ransomware": 3, "phishing": 2,
    "phát hành": 1, "ra mắt": 1, "cập nhật": 1,

    # === KINH TẾ ===
    "gdp": 4, "lạm phát": 3, "lãi suất": 3, "tăng trưởng kinh tế": 3,
    "chứng khoán": 3, "thị trường chứng khoán": 3, "vn-index": 3,
    "đầu tư": 2, "fdi": 3, "startup": 3, "kỳ lân": 3,
    "xuất khẩu": 3, "nhập khẩu": 2, "thương mại": 2, "thuế quan": 3,
    "ngân hàng": 2, "tín dụng": 2, "tỷ giá": 3, "usd": 2,
    "doanh nghiệp": 1, "tập đoàn": 1, "ipo": 3, "cổ phiếu": 2,
    "bất động sản": 2, "giá nhà": 2, "thị trường bds": 2,
    "kinh tế mỹ": 3, "kinh tế trung quốc": 3, "kinh tế việt nam": 3,
    "suy thoái": 3, "khủng hoảng": 3, "phục hồi kinh tế": 2,

    # === KHOA HỌC & KHÁM PHÁ ===
    "nghiên cứu": 3, "phát minh": 4, "khám phá": 3, "khoa học": 2,
    "vũ trụ": 4, "nasa": 4, "hành tinh": 3, "thiên văn": 3,
    "lỗ đen": 4, "sao chổi": 3, "thiên thạch": 3, "ufo": 3,
    "dna": 3, "gene": 3, "vaccine": 3, "y học": 2, "ung thư": 2,
    "thuốc mới": 3, "điều trị": 2, "bệnh hiếm gặp": 3,
    "biến đổi khí hậu": 3, "el nino": 3, "nhiệt độ trái đất": 3,
    "năng lượng tái tạo": 3, "hydrogen": 3, "pin mặt trời": 2,
    "hóa thạch": 3, "khủng long": 3, "tiến hóa": 2,
    "vật lý lượng tử": 4, "máy tính lượng tử": 4,

    # === XÃ HỘI & CHÍNH SÁCH ===
    "chính sách": 3, "luật mới": 3, "nghị quyết": 2, "quốc hội": 2,
    "thủ tướng": 2, "chính phủ": 1, "bộ trưởng": 1,
    "cải cách": 3, "đề xuất": 1, "dự thảo": 2,
    "tham nhũng": 3, "điều tra": 2, "bắt giữ": 2, "khởi tố": 2,
    "môi trường": 2, "ô nhiễm": 2, "rác thải": 2,
    "giáo dục": 2, "đại học": 1, "tuyển sinh": 1,
    "y tế": 2, "bệnh viện": 1, "bảo hiểm": 1,
    "tai nạn": 1, "thiên tai": 2, "lũ lụt": 2, "bão": 2,

    # === THẾ GIỚI & ĐỊA CHÍNH TRỊ ===
    "chiến tranh": 3, "xung đột": 3, "nato": 3, "liên hợp quốc": 2,
    "biển đông": 4, "đài loan": 3, "triều tiên": 3, "iran": 2,
    "nga ukraine": 4, "trung đông": 3, "israel": 3, "hamas": 2,
    "mỹ trung": 3, "donald trump": 3, "tổng thống": 2,
    "thương chiến": 3, "trừng phạt": 2, "cấm vận": 2,
    "asean": 2, "apec": 2, "g7": 2, "g20": 2,

    # === ĐIỀU HAY & LẠ ===
    "kỷ lục thế giới": 4, "lần đầu tiên trong lịch sử": 4,
    "chưa từng có": 3, "hiếm gặp": 3, "bí ẩn": 3,
    "kỳ lạ": 3, "độc đáo": 3, "thú vị": 2,
    "phá kỷ lục": 3, "đột phá": 3, "cách mạng": 2,
    "sự thật bất ngờ": 3, "giải mã": 2, "bí mật": 2,
    "sinh vật mới": 4, "loài mới": 4, "hóa thạch mới": 4,
    "hiện tượng lạ": 3, "xuất hiện hiếm": 3,
    "tại sao": 1, "như thế nào": 1, "giải thích": 1,
}

# ─── Nguồn ưu tiên (cộng điểm cho nguồn tin chất lượng) ─────────────────────
PRIORITY_SOURCES = {
    "GenK": 3,
    "Tinh Tế": 3,
    "GenK Mobile": 2,
    "VnExpress Số Hóa": 2,
    "VnExpress Khoa Học": 2,
    "MIT Technology Review": 2,
    "Sforum": 1,
    "BBC Tiếng Việt": 2,
}


def score_article(article: dict) -> float:
    """
    Chấm điểm bài báo. Điểm cao = chất lượng tốt, phù hợp sở thích.
    Điểm âm thấp = tin rác → lọc bỏ.
    """
    title = article.get("title", "").lower()
    summary = article.get("summary", "").lower()
    text = title + " " + summary
    source = article.get("source_name", "")

    score = 0.0

    # Trừ điểm từ khóa rác
    for kw in NEGATIVE_KEYWORDS:
        if kw in text:
            score -= 4
            break  # Chỉ phạt 1 lần cho category này

    # Cộng điểm từ khóa chất lượng
    for kw, pts in POSITIVE_KEYWORDS.items():
        if kw in text:
            score += pts

    # Ưu tiên nguồn tin yêu thích
    score += PRIORITY_SOURCES.get(source, 0)

    # Tiêu đề ngắn quá hoặc dài quá thường không tốt
    title_len = len(article.get("title", ""))
    if title_len < 15:
        score -= 2
    elif title_len > 120:
        score -= 1

    # Có tóm tắt thì tốt hơn
    if len(article.get("summary", "")) > 50:
        score += 0.5

    # Có ảnh thumbnail thì ưu tiên hơn
    if article.get("thumbnail"):
        score += 0.5

    return score


def filter_and_rank(articles: list, min_score: float = -3.0) -> list:
    """
    Lọc tin rác và sắp xếp theo điểm chất lượng + độ mới.
    Trả về danh sách bài đã được chấm điểm, tốt nhất lên đầu.
    """
    from datetime import datetime, timezone
    from dateutil import parser as dp

    scored = []
    for art in articles:
        q = score_article(art)
        if q < min_score:
            continue

        # Điểm thời gian: tin mới hơn được ưu tiên
        try:
            pub = dp.parse(art["pub_date"])
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            hours_ago = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
            # Tin trong 6h: +3 điểm, tin trong 12h: +1.5, tin trong 24h: +0.5
            if hours_ago < 6:
                recency = 3.0
            elif hours_ago < 12:
                recency = 1.5
            elif hours_ago < 24:
                recency = 0.5
            else:
                recency = 0.0
        except Exception:
            recency = 0.0

        total = q + recency
        scored.append((total, art))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [art for _, art in scored]


if __name__ == "__main__":
    # Test
    test_articles = [
        {"title": "ChatGPT ra mắt tính năng mới gây chấn động làng AI", "summary": "OpenAI vừa cập nhật...", "source_name": "GenK", "pub_date": "2026-06-11T10:00:00+07:00", "thumbnail": "x"},
        {"title": "Hot girl lộ hàng gây sốt mạng xã hội", "summary": "Người mẫu hot girl...", "source_name": "Kenh14", "pub_date": "2026-06-11T10:00:00+07:00"},
        {"title": "Khám phá bí ẩn lỗ đen lần đầu tiên trong lịch sử", "summary": "NASA vừa phát hiện...", "source_name": "VnExpress Khoa Học", "pub_date": "2026-06-11T09:00:00+07:00", "thumbnail": "x"},
        {"title": "Sale off 50% điện thoại Samsung", "summary": "Mua ngay hôm nay...", "source_name": "Sforum", "pub_date": "2026-06-11T08:00:00+07:00"},
    ]
    results = filter_and_rank(test_articles, min_score=-2)
    print("Kết quả sau lọc:")
    for art in results:
        print(f"  [{score_article(art):+.1f}] {art['title'][:60]}")
