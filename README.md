# Bản Tin Hằng Ngày v2 — Hướng dẫn triển khai

Mục tiêu: bản tin tự chạy 06:59 mỗi sáng trên GitHub, **không phụ thuộc MacBook
hay iMac có bật hay không**, đồng thời xuất bản một website ai cũng đọc được.

---

## ⚠️ Vì sao phải tạo repo MỚI

Repo `bot-news-cloud` hiện đang **private**. GitHub Pages chỉ miễn phí với repo
**public**, mà repo đó lại có lịch sử commit từng chứa token GitHub bị lộ — mở
public là lộ luôn. Vì vậy hãy tạo một repo mới, sạch.

---

## Bước 1 — Tạo repo public

1. Vào https://github.com/new
2. Repository name: **`ban-tin`**
3. Chọn **Public** → **Create repository**

> Muốn đặt tên khác cũng được, chỉ cần nhớ tên để làm Bước 4.

## Bước 2 — Tải code lên

1. Trong repo mới, bấm **Add file → Upload files**
2. Kéo thả **toàn bộ file** trong thư mục `bantin_v2` vào (trừ `email_config.json`)
3. Bấm **Commit changes**

Riêng file workflow phải tạo bằng tay vì thư mục `.github` bị Finder ẩn:

4. Vào tab **Actions → set up a workflow yourself**
5. Xoá hết nội dung mẫu, dán toàn bộ nội dung file `.github/workflows/daily-news.yml`
6. Đặt tên file là `daily-news.yml` → **Commit changes**

## Bước 3 — Nạp thông tin đăng nhập email

Vào **Settings → Secrets and variables → Actions → New repository secret**, tạo 3 secret:

| Tên | Giá trị |
|---|---|
| `GMAIL_ADDRESS` | `sanxuansan@gmail.com` |
| `GMAIL_PASSWORD` | App Password Gmail **mới** (16 ký tự) |
| `NEWS_RECIPIENT` | `sanxuansan@gmail.com` |

> 🔐 Bắt buộc tạo App Password **mới** tại https://myaccount.google.com/apppasswords
> và **thu hồi cái cũ** — mật khẩu cũ đang nằm dạng văn bản thường trong
> `email_config.json` và đã bị đóng gói ra ngoài theo file zip.

Sang tab **Variables** cùng trang, tạo 1 biến:

| Tên | Giá trị |
|---|---|
| `SITE_URL` | `https://xuansan1970.github.io/ban-tin/` |

## Bước 4 — Bật GitHub Pages

**Settings → Pages**
- Source: **Deploy from a branch**
- Branch: **main** · Folder: **/docs** → **Save**

Sau lần chạy đầu tiên, web sẽ sống tại `https://xuansan1970.github.io/ban-tin/`

## Bước 5 — Chạy thử

**Actions → Bản Tin Hằng Ngày → Run workflow**

Khoảng 3–5 phút sau: email về hộp thư, website lên sóng.

## Bước 6 — Dọn hệ thống cũ

Sau khi xác nhận bản mới chạy ổn 1–2 ngày:

- Trên **iMac**: `crontab -l | grep -v run_news.py | crontab -` để khỏi nhận 2 email trùng
- Trên repo `bot-news-cloud`: disable 2 workflow `Force Deploy to Render` và
  `Keep Render Alive` (Render đã bị suspend, chúng chỉ chạy vô ích)

---

## Chạy tay trên máy Mac (khi cần)

```bash
cd bantin_v2
python3 run_news_v2.py              # cào tin + gửi mail + dựng web
python3 run_news_v2.py --no-email   # chỉ dựng web, xem trước last_email.html
python3 run_news_v2.py --limit 2    # test nhanh, mỗi mục chỉ 2 nguồn
```

## Bản đồ file

| File | Vai trò |
|---|---|
| `run_news_v2.py` | Điều phối toàn bộ quy trình |
| `thumbnail_resolver.py` | Chuỗi 5 lớp tìm ảnh + kiểm tra link |
| `render_email.py` | Dựng email Dark Premium |
| `site_builder.py` + `site_template.py` | Dựng website tĩnh |
| `brand.py` | Bảng màu, tên thương hiệu, URL site |
| `mailer.py` | Gửi mail, đọc thông tin từ biến môi trường |
| `news_fetcher.py` | Đọc RSS + chấm điểm chất lượng |
| `sources.json` | Danh sách nguồn báo — thêm/bớt nguồn ở đây |

## Muốn chỉnh giao diện

- Đổi màu chuyên mục: `brand.py` → `CATEGORY_THEME`
- Đổi bố cục / CSS website: `site_template.py`
- Đổi bố cục email: `render_email.py`
- Đổi số tin mỗi mục: `sources.json` → `max_articles`
