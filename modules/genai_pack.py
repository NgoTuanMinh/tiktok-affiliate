"""
Một lần gọi Gemini (google.genai): script + hashtags + metadata + caption + A/B pack.
Có retry/backoff khi 429 và cache theo story_id.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import re
import time
from typing import Any, Dict, Optional

from google import genai
from google.genai import errors as genai_errors

from config import (
    DEFAULT_HASHTAGS,
    GEMINI_API_KEY,
    GEMINI_CACHE_ENABLED,
    GEMINI_CACHE_DIR,
    GEMINI_MAX_RETRIES,
    GEMINI_MODEL,
)
from modules.fallbacks import build_offline_content_pack


def _story_cache_key(story: dict, offer: dict) -> str:
    raw = "|".join(
        [
            str(story.get("url") or ""),
            str(story.get("title") or ""),
            str(story.get("content") or "")[:800],
            str(offer.get("offer_type") or ""),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def _cache_path(key: str) -> str:
    os.makedirs(GEMINI_CACHE_DIR, exist_ok=True)
    return os.path.join(GEMINI_CACHE_DIR, f"{key}.json")


def _load_cache(key: str) -> Optional[dict]:
    path = _cache_path(key)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _save_cache(key: str, data: dict) -> None:
    try:
        path = _cache_path(key)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _extract_json_object(text: str) -> Optional[dict]:
    if not text:
        return None
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def _is_retryable(e: BaseException) -> bool:
    msg = str(e).lower()
    if "429" in msg or "quota" in msg or "resource exhausted" in msg:
        return True
    if "503" in msg or "unavailable" in msg or "timeout" in msg:
        return True
    code = getattr(e, "code", None)
    if isinstance(e, genai_errors.APIError) and code in (429, 500, 503):
        return True
    return False


def _build_combined_prompt(story: dict, offer: dict) -> str:
    title = story.get("title", "Câu chuyện bí ẩn")
    content = story.get("content", "")
    offer_block = ""
    if offer:
        offer_block = f"""
NGỮ CẢNH AFFILIATE (product-first):
- Offer: {offer.get('name', '')}
- Pain point: {offer.get('pain_point', '')}
- Benefit: {offer.get('benefit', '')}
- CTA gợi ý: {offer.get('cta_hint', '')}
- Placeholder link trong caption: {offer.get('affiliate_link', '[DAN_LINK_AFFILIATE_VAO_DAY]')}
"""
    return f"""
Bạn là chuyên gia TikTok faceless storytelling (bí ẩn + tâm lý học) và affiliate mềm.

NHIỆM VỤ: Trả về DUY NHẤT một JSON hợp lệ (không markdown, không giải thích ngoài JSON).

DỮ LIỆU GỐC:
TIÊU ĐỀ: {title}
NỘI DUNG: {content}
{offer_block}

YÊU CẦU script (trường "script"):
- Kịch bản đọc lên 30-45 giây, tiếng Việt, giọng kể tự nhiên
- Hook 3-5s, thân bài nhanh, kết CTA mềm hướng bấm link bio/giỏ hàng/mô tả (không bán hàng lộ liễu)
- 180-250 từ

YÊU CẦU hashtags (trường "hashtags"):
- Một dòng, 20-30 hashtag cách nhau bằng space, bắt đầu #, có mix trending + chủ đề bí ẩn/tâm lý

YÊU CẦU youtube_metadata (object):
- "title": < 60 ký tự, có #shorts
- "description": 150-220 ký tự + hashtag shorts/storytime

YÊU CẦU tiktok_caption:
- 450-650 ký tự, hook đầu, lợi ích offer tự nhiên, CTA, cuối có block hashtag

YÊU CẦU ab_test_pack (object):
- hook_variants: đúng 3 chuỗi ngắn
- caption_variants: đúng 3 caption (có thể dùng placeholder link như trong offer)
- pinned_comment_variants: đúng 3 comment ghim CTA

Schema JSON:
{{
  "script": "...",
  "hashtags": "#fyp ...",
  "youtube_metadata": {{ "title": "...", "description": "..." }},
  "tiktok_caption": "...",
  "ab_test_pack": {{
    "hook_variants": ["","",""],
    "caption_variants": ["","",""],
    "pinned_comment_variants": ["","",""]
  }}
}}
"""


def _normalize_pack(raw: dict, story: dict, offer: dict) -> dict:
    script = (raw.get("script") or "").strip()
    if not script:
        return build_offline_content_pack(story, offer)

    hashtags = (raw.get("hashtags") or "").strip()
    if len(hashtags.split()) < 10:
        hashtags = (hashtags + " " + DEFAULT_HASHTAGS).strip()

    ym = raw.get("youtube_metadata") or {}
    if not isinstance(ym, dict):
        ym = {}
    youtube_meta = {
        "title": str(ym.get("title") or story.get("title", ""))[:80],
        "description": str(ym.get("description") or "")[:500],
    }

    tiktok_caption = (raw.get("tiktok_caption") or "").strip()
    if not tiktok_caption or "#" not in tiktok_caption:
        from modules.fallbacks import fallback_tiktok_caption

        tiktok_caption = fallback_tiktok_caption(script, story.get("title", ""), offer)

    ab = raw.get("ab_test_pack") or {}
    if not isinstance(ab, dict):
        ab = {}
    for key in ("hook_variants", "caption_variants", "pinned_comment_variants"):
        lst = ab.get(key)
        if not isinstance(lst, list):
            lst = []
        ab[key] = [str(x).strip() for x in lst[:3] if str(x).strip()]
    while len(ab["hook_variants"]) < 3:
        ab["hook_variants"].append("Bạn đã bao giờ tự hỏi vì sao tâm lý lại dễ bị thao túng?")
    while len(ab["caption_variants"]) < 3:
        ab["caption_variants"].append(tiktok_caption[:600])
    while len(ab["pinned_comment_variants"]) < 3:
        ab["pinned_comment_variants"].append(
            "Mình để link ở bio/giỏ hàng, bạn xem thử nhé."
        )

    return {
        "script": script,
        "hashtags": hashtags,
        "youtube_metadata": youtube_meta,
        "tiktok_caption": tiktok_caption,
        "ab_test_pack": ab,
        "source": "gemini",
    }


def _generate_raw_with_retry(client: genai.Client, prompt: str) -> Optional[dict]:
    delay = float(os.getenv("GEMINI_RETRY_BASE_SECONDS", "2"))
    last_err: Optional[BaseException] = None
    for attempt in range(GEMINI_MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )
            text = (response.text or "").strip()
            parsed = _extract_json_object(text)
            if parsed:
                return parsed
            print("⚠️ Gemini trả về không parse được JSON, thử lại...")
        except Exception as e:
            last_err = e
            if _is_retryable(e):
                wait = delay + random.uniform(0, 1.5)
                print(
                    f"⚠️ Gemini rate limit/quota (429), chờ {wait:.1f}s "
                    f"(lần {attempt + 1}/{GEMINI_MAX_RETRIES})..."
                )
                time.sleep(wait)
                delay = min(delay * 2, 120)
            else:
                print(f"⚠️ Lỗi Gemini: {e}")
                break
    if last_err:
        print(f"⚠️ Hết retry Gemini: {last_err}")
    return None


def generate_content_pack(story: dict, offer: dict) -> dict:
    """
    Trả về dict: script, hashtags, youtube_metadata, tiktok_caption, ab_test_pack, source.
    """
    key = _story_cache_key(story, offer)
    if GEMINI_CACHE_ENABLED:
        cached = _load_cache(key)
        if cached and cached.get("script"):
            cached["source"] = "cache"
            return cached

    if not GEMINI_API_KEY or not str(GEMINI_API_KEY).strip():
        pack = build_offline_content_pack(story, offer)
        if GEMINI_CACHE_ENABLED:
            _save_cache(key, pack)
        return pack

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = _build_combined_prompt(story, offer)
    raw = _generate_raw_with_retry(client, prompt)

    if raw:
        pack = _normalize_pack(raw, story, offer)
    else:
        pack = build_offline_content_pack(story, offer)

    if GEMINI_CACHE_ENABLED:
        _save_cache(key, pack)
    return pack
