# main.py
import asyncio
import os
import sys
from datetime import datetime

# Thêm thư mục hiện tại vào path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.scraper import StoryScraper
from modules.script_generator import generate_script
from modules.seo_generator import (
    generate_hashtags,
    generate_youtube_metadata,
    generate_affiliate_caption,
    generate_ab_test_pack,
)
from modules.video_generator import create_video
from modules.exporter import export_video_package
from modules.offer_selector import choose_offer
from config import OUTPUT_DIR

# Tạo thư mục output nếu chưa có
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def run_pipeline():
    """Chạy toàn bộ pipeline cho 1 video"""
    
    print("\n" + "="*60)
    print(f"🚀 BẮT ĐẦU PIPELINE - {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
    print("="*60)
    
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
    print(f"   🔗 Link: {offer.get('affiliate_link', '[DAN_LINK_AFFILIATE_VAO_DAY]')}")
    
    # Bước 2: Sinh kịch bản
    print("\n✍️ Bước 2: Sinh kịch bản với Gemini...")
    script = generate_script(story, offer=offer)
    print(f"   ✅ Đã sinh kịch bản ({len(script)} ký tự)")
    print(f"   📝 Preview: {script[:100]}...")
    
    # Bước 3: Sinh SEO
    print("\n🏷️ Bước 3: Sinh hashtags và metadata...")
    hashtags = generate_hashtags(script, story['title'])
    youtube_meta = generate_youtube_metadata(story['title'], script)
    tiktok_caption = generate_affiliate_caption(script, story['title'], offer)
    ab_test_pack = generate_ab_test_pack(script, story['title'], offer, hashtags)
    print(f"   ✅ Đã sinh {len(hashtags.split())} hashtags")
    print(f"   📺 YouTube title: {youtube_meta.get('title', 'N/A')[:50]}...")
    print(f"   🧲 Đã sinh caption affiliate ({len(tiktok_caption)} ký tự)")
    print("   🧪 Đã tạo A/B test pack (hooks/captions/comments)")
    
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
    
    print("\n" + "="*60)
    print("🎉 PIPELINE HOÀN TẤT!")
    print("="*60)
    print(f"\n📂 THƯ MỤC OUTPUT: {folder_path}")
    print("\n📋 CÁC BƯỚC TIẾP THEO:")
    print("   1. Mở thư mục output")
    print("   2. Đọc file HUONG_DAN_LAY_LINK_AFFILIATE.txt để lấy link")
    print("   3. Đọc file HUONG_DAN_DANG_BAI.txt để đăng video")
    print("   4. Dùng caption.txt để copy-paste nội dung")
    print("\n✨ Chúc bạn thành công!\n")

def main():
    """Chạy pipeline (hàm đồng bộ)"""
    asyncio.run(run_pipeline())

if __name__ == "__main__":
    main()