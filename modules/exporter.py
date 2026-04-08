# modules/exporter.py
import os
import json
import shutil
from datetime import datetime
from config import OUTPUT_DIR, AFFILIATE_PLATFORMS

def generate_affiliate_guide(story_title: str, story_content: str, niche: str = "storytelling") -> str:
    """Tạo hướng dẫn chi tiết để lấy link affiliate phù hợp"""
    
    # Phân tích nội dung để gợi ý sản phẩm
    content_lower = (story_title + " " + story_content).lower()
    
    suggested_products = []
    
    if any(word in content_lower for word in ["sách", "đọc", "truyện", "cuốn"]):
        suggested_products.append("📚 Sách (truyện trinh thám, tâm lý học, phát triển bản thân)")
    if any(word in content_lower for word in ["học", "bài học", "kiến thức", "biết"]):
        suggested_products.append("🎓 Khóa học online (kỹ năng mềm, sáng tạo nội dung)")
    if any(word in content_lower for word in ["tâm lý", "cảm xúc", "suy nghĩ"]):
        suggested_products.append("🧠 Sách tâm lý học, khóa học phát triển bản thân")
    if any(word in content_lower for word in ["bí ẩn", "ma", "kinh dị", "rùng rợn"]):
        suggested_products.append("👻 Truyện kinh dị, audio book, merchandise áo hình ma")
    
    if not suggested_products:
        suggested_products = ["📚 Sách tổng hợp", "🎧 Audio book", "🛍️ Merchandise (áo, móc khóa)"]
    
    guide = f"""
╔══════════════════════════════════════════════════════════════════╗
║          🔗 HƯỚNG DẪN LẤY LINK AFFILIATE CHO VIDEO NÀY          ║
╚══════════════════════════════════════════════════════════════════╝

📖 NỘI DUNG VIDEO:
Tiêu đề: {story_title}
Thể loại: {niche}

🎯 GỢI Ý SẢN PHẨM PHÙ HỢP (chọn 1-2 sản phẩm):
{chr(10).join([f"   {i+1}. {p}" for i, p in enumerate(suggested_products)])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 CÁCH LẤY LINK AFFILIATE TRÊN CÁC NỀN TẢNG:

1️⃣ TIKTOK SHOP (Ưu tiên số 1 - hoa hồng 10-20%)
   → Mở TikTok App → Tab "TikTok Shop" (icon giỏ hàng)
   → Tìm kiếm từ khóa: {"sách tâm lý học" if "tâm lý" in content_lower else "truyện trinh thám"}
   → Chọn sản phẩm có hoa hồng cao
   → Bấm "Get affiliate link" → Copy link

2️⃣ SHOPEE AFFILIATE (Hoa hồng 5-15%)
   → Truy cập: https://affiliate.shopee.vn
   → Đăng nhập → Tìm sản phẩm
   → Bấm "Lấy link" → Copy

3️⃣ TIKI AFFILIATE (Hoa hồng 5-10%)
   → Truy cập: https://tiki.vn/affiliate
   → Tìm sách theo chủ đề → Lấy link

4️⃣ AMAZON ASSOCIATES (Hoa hồng 4-10%)
   → Truy cập: https://affiliate-program.amazon.com
   → Tìm sản phẩm tiếng Anh → Lấy link

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧩 QUY TRÌNH KHUYẾN NGHỊ CHO BẠN (UPLOAD THỦ CÔNG, HẠN CHẾ BOT QUÉT):
   1) Tạo video bằng pipeline này
   2) Lấy link affiliate phù hợp và gắn vào caption / giỏ hàng
   3) Upload tay trên điện thoại, tránh hành vi tự động hóa
   4) Sau 24h cập nhật chỉ số vào daily_performance_template.csv

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CÁCH GẮN LINK KHI ĐĂNG VIDEO:

TRÊN TIKTOK:
   Bước 1: Chọn video → Màn hình đăng
   Bước 2: Bấm "Add link" → "Product"
   Bước 3: Dán link affiliate đã copy
   Bước 4: Bấm "Done"

TRÊN YOUTUBE SHORTS:
   → Dán link vào phần mô tả (description)
   → Hoặc để link trong comment đầu tiên

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 MẸO TĂNG CHUYỂN ĐỔI:
   • Gắn link sản phẩm liên quan TRỰC TIẾP đến nội dung video
   • Nhắc nhẹ nhàng trong video: "Link sách mình để ở phần mô tả nhé"
   • Đăng video vào khung giờ vàng: 19h-21h các ngày trong tuần

📌 Link các nền tảng affiliate:
   • TikTok Shop: {AFFILIATE_PLATFORMS.get('tiktok_shop', 'https://www.tiktok.com/shop')}
   • Shopee: {AFFILIATE_PLATFORMS.get('shopee', 'https://affiliate.shopee.vn')}
   • Tiki: {AFFILIATE_PLATFORMS.get('tiki', 'https://tiki.vn/affiliate')}
   • Amazon: {AFFILIATE_PLATFORMS.get('amazon', 'https://affiliate-program.amazon.com')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return guide

def export_video_package(
    video_path: str,
    story: dict,
    script: str,
    hashtags: str,
    offer: dict = None,
    tiktok_caption: str = "",
    youtube_meta: dict = None,
    ab_test_pack: dict = None,
):
    """Xuất toàn bộ file cần thiết vào folder"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = story['title'][:30].replace(' ', '_').replace('/', '_').replace('?', '')
    folder_name = f"{timestamp}_{safe_title}"
    folder_path = os.path.join(OUTPUT_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    # 1. Copy video
    video_dest = os.path.join(folder_path, "video.mp4")
    shutil.move(video_path, video_dest)
    
    # 2. Tạo caption (đã có sẵn để copy-paste)
    affiliate_link = (offer or {}).get("affiliate_link", "[DAN_LINK_AFFILIATE_VAO_DAY]")
    offer_name = (offer or {}).get("name", "tai nguyen lien quan")
    suggested_keywords = (offer or {}).get("suggested_search_keywords", [])

    caption = f"""{script}

📖 {story['title']}

💬 Bạn nghĩ sao về câu chuyện này? Comment nhé!

👉 Link {offer_name}: {affiliate_link}

{hashtags}
"""
    with open(os.path.join(folder_path, "caption.txt"), "w", encoding="utf-8") as f:
        f.write(caption)

    # 2b. Caption tối ưu affiliate conversion cho TikTok
    if tiktok_caption:
        with open(os.path.join(folder_path, "caption_affiliate.txt"), "w", encoding="utf-8") as f:
            f.write(tiktok_caption)
    
    # 3. Hashtags chỉ (dễ copy)
    with open(os.path.join(folder_path, "hashtags_only.txt"), "w", encoding="utf-8") as f:
        f.write(hashtags)
    
    # 4. 🔥 HƯỚNG DẪN LẤY LINK AFFILIATE (QUAN TRỌNG) 🔥
    affiliate_guide = generate_affiliate_guide(story['title'], story.get('content', ''))
    with open(os.path.join(folder_path, "HUONG_DAN_LAY_LINK_AFFILIATE.txt"), "w", encoding="utf-8") as f:
        f.write(affiliate_guide)

    # 4b. Gợi ý nhanh để bạn lấy link đúng offer
    if suggested_keywords:
        quick = [
            "GOI Y LAY LINK AFFILIATE (NHANH)",
            f"- Offer: {offer_name}",
            "- Tu khoa tim tren TikTok Shop/Shopee/Tiki:",
        ]
        for kw in suggested_keywords:
            quick.append(f"  - {kw}")
        quick.append("")
        quick.append("Sau khi lay duoc link, dan vao:")
        quick.append("- caption_affiliate.txt (uu tien)")
        quick.append("- hoac caption.txt")
        quick.append(f"Placeholder can thay: {affiliate_link}")
        with open(os.path.join(folder_path, "GOI_Y_LAY_LINK.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(quick))
    
    # 5. Hướng dẫn đăng bài nhanh
    quick_guide = """
╔════════════════════════════════════════════════════════╗
║     📱 HƯỚNG DẪN ĐĂNG BÀI NHANH (5 PHÚT)             ║
╚════════════════════════════════════════════════════════╝

1. Mở TikTok → Bấm dấu +
2. Chọn video.mp4 từ folder này
3. Copy nội dung từ caption.txt → Dán vào ô caption
4. Mở file HUONG_DAN_LAY_LINK_AFFILIATE.txt → Lấy link → Gắn vào video
5. Chọn ảnh bìa đẹp
6. Bấm "Schedule" → Chọn 19h-21h (hoặc Post nếu đúng giờ)

⏰ Khung giờ vàng: 19h-21h các ngày trong tuần, 9h-11h cuối tuần
"""
    with open(os.path.join(folder_path, "HUONG_DAN_DANG_BAI.txt"), "w", encoding="utf-8") as f:
        f.write(quick_guide)
    
    # 6. Metadata để theo dõi
    metadata = {
        "story_title": story['title'],
        "story_source": story.get('source', 'unknown'),
        "script": script,
        "created_at": timestamp,
        "hashtags": hashtags,
        "folder_path": folder_path,
        "offer": offer or {},
        "youtube_metadata": youtube_meta or {},
        "tracking": {
            "campaign_id": f"tt_{timestamp}",
            "views": 0,
            "clicks": 0,
            "orders": 0,
            "revenue": 0,
        },
    }
    with open(os.path.join(folder_path, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # 7. File checklist đăng bài nhanh có tracking
    posting_pack = f"""CHECKLIST DANG BAI AFFILIATE

1) Upload video.mp4
2) Dung uu tien: caption_affiliate.txt (neu co), neu khong dung caption.txt
3) Gan link affiliate:
   - Offer: {offer_name}
   - Link: {affiliate_link}
4) Pin 1 comment CTA: "Minh de link o bio/giỏ hang, ban co the xem ngay."
5) Sau 24h cap nhat performance vao metadata.json (views/clicks/orders/revenue)
"""
    with open(os.path.join(folder_path, "POSTING_CHECKLIST.txt"), "w", encoding="utf-8") as f:
        f.write(posting_pack)

    # 8. A/B test pack để đăng tay tối ưu conversion
    if ab_test_pack:
        ab_path = os.path.join(folder_path, "AB_TEST_PACK.txt")
        hooks = ab_test_pack.get("hook_variants", [])
        captions = ab_test_pack.get("caption_variants", [])
        comments = ab_test_pack.get("pinned_comment_variants", [])
        lines = [
            "A/B TEST PACK - FACELESS AI STORYTELLING",
            "",
            "HOOK VARIANTS:",
        ]
        for idx, hook in enumerate(hooks, start=1):
            lines.append(f"{idx}. {hook}")
        lines.append("")
        lines.append("CAPTION VARIANTS:")
        for idx, cap in enumerate(captions, start=1):
            lines.append(f"{idx}. {cap}")
            lines.append("")
        lines.append("PINNED COMMENT VARIANTS:")
        for idx, com in enumerate(comments, start=1):
            lines.append(f"{idx}. {com}")
        lines.append("")
        lines.append("GOI Y SU DUNG:")
        lines.append("- Ngay 1: dung variant 1")
        lines.append("- Ngay 2: dung variant 2")
        lines.append("- Ngay 3: dung variant 3")
        lines.append("- Sau 72h, chon variant co click/order tot nhat.")
        with open(ab_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        # Luu JSON de ban co the xu ly data sau nay
        with open(os.path.join(folder_path, "ab_test_pack.json"), "w", encoding="utf-8") as f:
            json.dump(ab_test_pack, f, indent=2, ensure_ascii=False)

    # 9. Bảng log hiệu suất ngày (manual update)
    perf_csv = os.path.join(folder_path, "daily_performance_template.csv")
    with open(perf_csv, "w", encoding="utf-8") as f:
        f.write(
            "date,platform,variant,views,clicks,orders,revenue,notes\n"
            "YYYY-MM-DD,tiktok,variant_1,0,0,0,0,\n"
        )
    
    print(f"\n✅ ĐÃ XUẤT THÀNH CÔNG!")
    print(f"📁 Thư mục: {folder_path}")
    print(f"🎬 Video: video.mp4")
    print(f"🔗 Hướng dẫn lấy link: HUONG_DAN_LAY_LINK_AFFILIATE.txt")
    
    return folder_path