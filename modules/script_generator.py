# modules/script_generator.py
"""Kịch bản: pipeline chính dùng modules.genai_pack (1 request). File này giữ fallback offline."""
from __future__ import annotations

from typing import Optional

from modules.fallbacks import fallback_script


def generate_script(story: dict, offer: Optional[dict] = None) -> str:
    """Chỉ dùng khi cần script offline nhanh; main.py gọi genai_pack.generate_content_pack."""
    return fallback_script(story, offer)
