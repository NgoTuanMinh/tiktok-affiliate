# modules/seo_generator.py
"""SEO/A/B: pipeline chính dùng genai_pack (1 request Gemini). Các hàm dưới là fallback offline."""
from __future__ import annotations

from typing import Dict

from config import DEFAULT_HASHTAGS
from modules.fallbacks import (
    ab_test_fallback,
    fallback_tiktok_caption,
    fallback_youtube_meta,
)


def generate_hashtags(script: str, title: str) -> str:
    base = f"{DEFAULT_HASHTAGS} #fyp #viral #tiktokvietnam #shorts #storytime"
    return f"{base} #bi_an #tam_ly_hoc #cau_chuyen"


def generate_affiliate_caption(script: str, title: str, offer: dict) -> str:
    return fallback_tiktok_caption(script, title, offer)


def generate_ab_test_pack(
    script: str, title: str, offer: dict, hashtags: str
) -> Dict:
    return ab_test_fallback(script, title, offer, hashtags)


def generate_youtube_metadata(title: str, script: str) -> dict:
    return fallback_youtube_meta(title, script)
