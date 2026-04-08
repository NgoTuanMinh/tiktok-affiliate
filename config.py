# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# Gemini (google-genai SDK) — một request gộp trong genai_pack
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()
GEMINI_MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "5"))
GEMINI_CACHE_ENABLED = os.getenv("GEMINI_CACHE", "true").lower() in (
    "1",
    "true",
    "yes",
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GEMINI_CACHE_DIR = os.path.join(BASE_DIR, ".cache", "gemini")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
MUSIC_DIR = os.path.join(ASSETS_DIR, "background_music")
AVATAR_DIR = os.path.join(ASSETS_DIR, "avatars")

# Video settings
VIDEO_DURATION = 45  # giây
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 24

# Ngách settings
NICHE = "storytelling"
DEFAULT_HASHTAGS = "#bi_an #tam_ly_hoc #cau_chuyen #xuhuong #fyp"

# Faceless AI Storytelling niche focus
TARGET_NICHE = "faceless_ai_storytelling"
TARGET_TOPIC = "bi_an_va_tam_ly_hoc"

# Affiliate platforms (để hướng dẫn lấy link)
AFFILIATE_PLATFORMS = {
    "tiktok_shop": "https://www.tiktok.com/shop",
    "amazon": "https://affiliate-program.amazon.com",
    "tiki": "https://tiki.vn/affiliate",
    "shopee": "https://affiliate.shopee.vn",
    "lazada": "https://lazada.vn/affiliate"
}

# Offer catalog để hệ thống chọn "product-first" trước khi viết script
OFFER_CATALOG = [
    {
        "offer_type": "audiobook",
        "name": "Sách nói phát triển bản thân",
        "pain_point": "khó duy trì thói quen học mỗi ngày",
        "benefit": "nghe mọi lúc, hấp thụ kiến thức nhanh, duy trì động lực",
        "cta_hint": "Link sách nói mình để ở bio/giỏ hàng, vào nghe thử ngay.",
    },
    {
        "offer_type": "course",
        "name": "Khóa học tâm lý học ứng dụng",
        "pain_point": "khó hiểu cảm xúc bản thân và người khác",
        "benefit": "nắm nguyên tắc tâm lý để giao tiếp và ra quyết định tốt hơn",
        "cta_hint": "Mình để link khóa học ở phần mô tả, bấm vào xem lộ trình.",
    },
    {
        "offer_type": "meditation_app",
        "name": "Ứng dụng thiền định và ngủ sâu",
        "pain_point": "mất ngủ, lo âu, đầu óc quá tải",
        "benefit": "thiền có hướng dẫn 10 phút/ngày, ngủ tốt và giảm stress",
        "cta_hint": "Link app thiền mình để sẵn, tải về trải nghiệm thử 7 ngày.",
    },
    {
        "offer_type": "self_help_course",
        "name": "Khóa học phát triển bản thân",
        "pain_point": "thiếu kỷ luật và mục tiêu rõ ràng",
        "benefit": "xây hệ thống thói quen và tư duy để tăng hiệu suất sống",
        "cta_hint": "Mình có để link khóa học ở bio, xem review rồi quyết định.",
    },
]