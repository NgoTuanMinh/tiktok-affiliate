# TikTok Affiliate Pipeline (Faceless AI Storytelling)

Pipeline này giúp bạn:

- Tạo video faceless theo ngách **Bí ẩn & Tâm lý học**
- Sinh caption/hashtag/biến thể A/B test
- Xuất bộ hướng dẫn lấy và gắn link affiliate
- Bạn **tự upload thủ công** lên TikTok (không auto-post)

## 1) Cài đặt lần đầu

### Bước 1: Tạo môi trường và cài thư viện

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### Bước 2: Tạo file `.env`

```env
GEMINI_API_KEY=your_key_here
PEXELS_API_KEY=your_pexels_key_here

# TTS (tuỳ chọn): ElevenLabs giọng hay hơn
# Nếu không set, hệ thống sẽ fallback Edge TTS (miễn phí)
TTS_PROVIDER=elevenlabs
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=your_voice_id_here

# Optional tinh chỉnh chất giọng
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
ELEVENLABS_STABILITY=0.5
ELEVENLABS_SIMILARITY_BOOST=0.75
ELEVENLABS_STYLE=0.0
ELEVENLABS_SPEAKER_BOOST=true
```

Ghi chú: **không cần** để link affiliate trong `.env`. Pipeline sẽ xuất video trước, sau đó bạn tự chọn link phù hợp và dán vào `caption_affiliate.txt`/caption khi đăng.

### Bước 3 (tùy chọn): Chuẩn bị assets

```bash
mkdir -p assets/background_music
mkdir -p assets/avatars
```

- Nhạc nền tùy chọn: tải từ [freepd.com](https://freepd.com/) rồi lưu vào:
  - `assets/background_music/mystery.mp3`

## 2) Chạy pipeline

```bash
python main.py
```

Sau khi chạy xong, mở thư mục `output/` và chọn folder mới nhất.

## 3) Luồng pipeline hiện tại (product-first)

1. Scrape story (Reddit + fallback)
2. Chọn offer affiliate phù hợp trước
3. Sinh script có CTA affiliate tự nhiên
4. Sinh SEO (hashtags, caption affiliate, A/B test pack)
5. Render video faceless
6. Xuất package để bạn đăng tay

## 4) File output quan trọng

Mỗi lần chạy sẽ tạo 1 folder trong `output/` gồm:

- `video.mp4`: video đăng TikTok
- `caption_affiliate.txt`: caption ưu tiên để đăng
- `caption.txt`: caption dự phòng
- `hashtags_only.txt`: hashtags copy nhanh
- `AB_TEST_PACK.txt`: 3 hook + 3 caption + 3 comment ghim để test
- `ab_test_pack.json`: dữ liệu A/B test dạng JSON
- `daily_performance_template.csv`: template cập nhật view/click/order/revenue
- `POSTING_CHECKLIST.txt`: checklist đăng tay
- `HUONG_DAN_LAY_LINK_AFFILIATE.txt`: hướng dẫn lấy link affiliate
- `HUONG_DAN_DANG_BAI.txt`: hướng dẫn đăng nhanh
- `metadata.json`: metadata + tracking theo campaign

## 5) Quy trình đăng tay khuyến nghị (không bật 24/24)

1. Chạy `python main.py` trước khung giờ đẹp 10-20 phút
2. Lấy link affiliate theo `HUONG_DAN_LAY_LINK_AFFILIATE.txt`
3. Dùng `caption_affiliate.txt` + gắn link
4. Upload thủ công trên điện thoại
5. Ghim comment CTA theo `AB_TEST_PACK.txt`

## 5.1) Flow chi tiết (từng bước để làm theo)

### 1) Trước giờ đăng 10–20 phút

Chạy pipeline:

```bash
python main.py
```

### 2) Mở folder output mới nhất

Trong `output/...` bạn sẽ thấy các file chính:

- `video.mp4`: video để upload
- `GOI_Y_LAY_LINK.txt` + `HUONG_DAN_LAY_LINK_AFFILIATE.txt`: hướng dẫn + từ khóa tìm sản phẩm/link
- `caption_affiliate.txt`: caption tối ưu chuyển đổi để copy đăng
- `AB_TEST_PACK.txt`: 3 variant hook/caption/comment để bạn test

### 3) Lấy link affiliate (thủ công)

- Vào TikTok Shop / Shopee / Tiki...
- Tìm sản phẩm theo từ khóa trong `GOI_Y_LAY_LINK.txt`
- Copy link affiliate (hoặc chuẩn bị gắn link qua tính năng “Add link/Product” trên TikTok)

### 4) Chuẩn bị caption để đăng

Chọn 1 variant trong `AB_TEST_PACK.txt` (ví dụ variant 1), rồi:

- Nếu bạn **dán URL vào caption**: thay placeholder `[DAN_LINK_AFFILIATE_VAO_DAY]` trong `caption_affiliate.txt` bằng link thật
- Nếu bạn **gắn link kiểu “Add link/Product”**: không cần dán URL, nhưng hãy sửa CTA trong `caption_affiliate.txt` thành “mình để ở giỏ hàng/Add link”

### 5) Upload thủ công lên TikTok (tránh bot quét)

- Upload `video.mp4` trên điện thoại
- Dán caption từ `caption_affiliate.txt`
- Gắn link bằng “Add link/Product” (nếu dùng TikTok Shop)
- Ghim comment CTA theo `AB_TEST_PACK.txt`

### 6) Sau 24h (hoặc 48h) cập nhật số liệu

- Mở `daily_performance_template.csv`
- Điền `views / clicks / orders / revenue` theo dashboard Analytics + Affiliate

### 7) A/B test 3 ngày

- Ngày 1 dùng variant 1
- Ngày 2 dùng variant 2
- Ngày 3 dùng variant 3

Sau đó giữ variant có `clicks/orders/revenue` tốt nhất.

## 6) Vòng 2: Tối ưu chuyển đổi bằng A/B test

Gợi ý chạy 3 ngày:

- Ngày 1: dùng variant 1
- Ngày 2: dùng variant 2
- Ngày 3: dùng variant 3

Mỗi ngày cập nhật `daily_performance_template.csv`:

- `views`
- `clicks`
- `orders`
- `revenue`

Sau 72 giờ, giữ lại variant có hiệu suất tốt nhất.

## 7) Vận hành hằng ngày (nhanh)

- Chạy pipeline: 2-5 phút (tùy thời gian render)
- Rà caption + gắn link: 2-3 phút
- Upload thủ công TikTok: 2-3 phút
- Tổng: khoảng 10 phút/ngày

