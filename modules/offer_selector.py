import random
from typing import Dict

from config import OFFER_CATALOG


def choose_offer(story: Dict) -> Dict:
    """
    Chọn offer affiliate trước khi viết script (product-first).
    Ưu tiên map theo từ khóa nội dung, nếu không có thì random.
    """
    content = f"{story.get('title', '')} {story.get('content', '')}".lower()

    scored = []
    for offer in OFFER_CATALOG:
        score = 0
        offer_type = offer.get("offer_type", "")
        if "tâm lý" in content and offer_type in {"course", "self_help_course"}:
            score += 2
        if any(k in content for k in ["mất ngủ", "lo âu", "stress", "sợ"]):
            if offer_type == "meditation_app":
                score += 3
        if any(k in content for k in ["bí ẩn", "câu chuyện", "truyện"]):
            if offer_type == "audiobook":
                score += 2
        if any(k in content for k in ["thói quen", "kỷ luật", "bài học"]):
            if offer_type in {"self_help_course", "course"}:
                score += 2

        scored.append((score, offer))

    scored.sort(key=lambda x: x[0], reverse=True)
    best_score = scored[0][0] if scored else 0
    candidates = [o for s, o in scored if s == best_score] if scored else []
    selected = random.choice(candidates) if candidates else random.choice(OFFER_CATALOG)

    offer_type = selected["offer_type"]
    affiliate_link = "[DAN_LINK_AFFILIATE_VAO_DAY]"

    keyword_map = {
        "audiobook": ["sách nói", "audiobook", "phát triển bản thân"],
        "course": ["khóa học tâm lý học", "tâm lý học ứng dụng", "giao tiếp"],
        "meditation_app": ["app thiền", "thiền định", "ngủ sâu", "giảm stress"],
        "self_help_course": ["khóa học phát triển bản thân", "thói quen", "kỷ luật"],
    }
    suggested_keywords = keyword_map.get(offer_type, [])

    return {
        **selected,
        "affiliate_link": affiliate_link,
        "suggested_search_keywords": suggested_keywords,
    }

