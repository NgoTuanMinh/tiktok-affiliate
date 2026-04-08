# main.py
import asyncio
import os
import sys
from datetime import datetime

# Fix Unicode output on some Windows consoles (emoji, Vietnamese).
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Thêm thư mục hiện tại vào path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.scraper import StoryScraper
from modules.genai_pack import generate_content_pack
from modules.video_generator import create_video
from modules.exporter import export_video_package
from modules.offer_selector import choose_offer
from config import OUTPUT_DIR

# Tạo thư mục output nếu chưa có
os.makedirs(OUTPUT_DIR, exist_ok=True)


async def run_pipeline():
    """Chạy toàn bộ pipeline cho 1 video"""

    print("\n" + "=" * 60)
    print(f"🚀 BẮT ĐẦU PIPELINE - {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
    print("=" * 60)

    # Bước 1: Lấy ý tưởng câu chuyện
    print("\n📖 Bước 1: Lấy ý tưởng câu chuyện...")
    scraper = StoryScraper()
    story = scraper.get_random_story()
    print(f"   ✅ Đã lấy: {story['title']}")
    print(f"   📍 Nguồn: {story.get('source', 'unknown')}")

    # Bước 1b: Chọn offer affiliate trước khi viết script (product-first)
    print("\n🛍️ Bước 1b: Chọn offer affiliate phù hợp...")
    offer = choose_offer(story)
    print(f"   ✅ Offer: {offer.get('name', 'N/A')}")
    print(f"   🔗 Placeholder: {offer.get('affiliate_link', '[DAN_LINK_AFFILIATE_VAO_DAY]')}")

    # Bước 2+3: Một lần gọi Gemini — script + SEO + caption + A/B (giảm 429)
    print("\n✍️ Bước 2–3: Sinh nội dung (Gemini 1 request / cache / fallback)...")
    pack = generate_content_pack(story, offer)
    script = pack["script"]
    hashtags = pack["hashtags"]
    youtube_meta = pack["youtube_metadata"]
    tiktok_caption = pack["tiktok_caption"]
    ab_test_pack = pack["ab_test_pack"]
    print(f"   📌 Nguồn nội dung: {pack.get('source', 'unknown')}")
    print(f"   ✅ Kịch bản ({len(script)} ký tự)")
    print(f"   📝 Preview: {script[:100]}...")
    print(f"   ✅ Hashtags: {len(hashtags.split())} từ")
    print(f"   📺 YouTube title: {youtube_meta.get('title', 'N/A')[:50]}...")
    print(f"   🧲 Caption affiliate ({len(tiktok_caption)} ký tự)")
    print("   🧪 A/B pack: hooks/captions/comments")

    # Bước 4: Tạo video
    print("\n🎬 Bước 4: Tạo video (có thể mất 2-3 phút)...")
    video_path = "temp_video.mp4"
    await create_video(script, video_path)
    print(f"   ✅ Đã tạo video: {video_path}")

    # Bước 5: Xuất folder
    print("\n📁 Bước 5: Xuất folder output...")
    folder_path = export_video_package(
        video_path=video_path,
        story=story,
        script=script,
        hashtags=hashtags,
        offer=offer,
        tiktok_caption=tiktok_caption,
        youtube_meta=youtube_meta,
        ab_test_pack=ab_test_pack,
    )

    print("\n" + "=" * 60)
    print("🎉 PIPELINE HOÀN TẤT!")
    print("=" * 60)
    print(f"\n📂 THƯ MỤC OUTPUT: {folder_path}")
    print("\n📋 CÁC BƯỚC TIẾP THEO:")
    print("   1. Mở thư mục output")
    print("   2. Đọc GOI_Y_LAY_LINK.txt + HUONG_DAN_LAY_LINK_AFFILIATE.txt")
    print("   3. Dán link thật vào caption_affiliate.txt rồi đăng tay")
    print("   4. Dùng AB_TEST_PACK.txt để test variant")
    print("\n✨ Chúc bạn thành công!\n")


def main():
    """Chạy pipeline (hàm đồng bộ)"""
    asyncio.run(run_pipeline())


if __name__ == "__main__":
    main()
