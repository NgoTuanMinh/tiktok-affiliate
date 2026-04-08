"""Fallback nội dung khi không gọi được Gemini (offline / lỗi API)."""
from __future__ import annotations

from typing import Any, Dict, Optional

from config import DEFAULT_HASHTAGS


def fallback_script(story: dict, offer: Optional[dict] = None) -> str:
    cta = (
        offer.get("cta_hint", "Mình để link tài nguyên liên quan ở bio nhé!")
        if offer
        else "Mình để link tài nguyên liên quan ở bio nhé!"
    )
    return f"""Bạn có biết? {story.get('title', 'Câu chuyện này')}

{story.get('content', '')[:200]}

Điều này khiến nhiều người bất ngờ đấy! {cta}"""


def ab_test_fallback(
    script: str, title: str, offer: dict, hashtags: str
) -> Dict[str, Any]:
    offer_name = offer.get("name", "tài nguyên liên quan")
    cta_hint = offer.get("cta_hint", "Mình để link ở bio/giỏ hàng, bấm vào xem nhé.")
    affiliate_link = offer.get("affiliate_link", "[DAN_LINK_AFFILIATE_VAO_DAY]")
    hooks = [
        f"Bạn có bao giờ tự hỏi vì sao {title.lower()}?",
        "Một hiệu ứng tâm lý có thể đang âm thầm điều khiển quyết định của bạn.",
        "Câu chuyện này nghe như hư cấu, nhưng lại phản ánh tâm lý rất thật.",
    ]
    captions = [
        f"{hooks[0]}\n\n{script[:220]}...\n\n{cta_hint}\nLink: {affiliate_link}\n\n{hashtags}",
        f"{hooks[1]}\n\n{script[:220]}...\n\nNếu muốn hiểu sâu hơn, mình để {offer_name} ở link nhé.\nLink: {affiliate_link}\n\n{hashtags}",
        f"{hooks[2]}\n\n{script[:220]}...\n\nXem thêm tài nguyên mình dùng tại đây: {affiliate_link}\n\n{hashtags}",
    ]
    comments = [
        f"Link {offer_name} mình để ở bio/giỏ hàng nhé, vào xem chi tiết.",
        'Ai muốn mình tổng hợp thêm tài nguyên cùng chủ đề thì comment "link".',
        f"Bạn có thể xem thử trước ở đây: {affiliate_link}",
    ]
    return {
        "hook_variants": hooks,
        "caption_variants": captions,
        "pinned_comment_variants": comments,
    }


def fallback_tiktok_caption(script: str, title: str, offer: dict) -> str:
    offer_name = offer.get("name", "tài nguyên liên quan")
    benefit = offer.get("benefit", "")
    cta_hint = offer.get("cta_hint", "Mình để link ở bio/giỏ hàng, bấm vào xem nhé.")
    affiliate_link = offer.get("affiliate_link", "[DAN_LINK_AFFILIATE_VAO_DAY]")
    return (
        f"{title}\n\n"
        f"Nếu bạn từng thấy mình trong câu chuyện này, thử {offer_name} để {benefit}. "
        f"{cta_hint}\n"
        f"Link: {affiliate_link}\n\n"
        f"{DEFAULT_HASHTAGS}"
    )


def fallback_youtube_meta(title: str, script: str) -> dict:
    return {
        "title": title[:55] + " #shorts",
        "description": script[:180] + "\n\n#storytime #bi_an #shorts",
    }


def build_offline_content_pack(story: dict, offer: dict) -> dict:
    """Một pack đầy đủ không cần Gemini."""
    script = fallback_script(story, offer)
    hashtags = (
        f"{DEFAULT_HASHTAGS} #fyp #viral #tiktokvietnam #shorts "
        "#tam_su #kham_pha #storytime"
    )
    youtube_meta = fallback_youtube_meta(story.get("title", ""), script)
    tiktok_caption = fallback_tiktok_caption(script, story.get("title", ""), offer)
    ab_test_pack = ab_test_fallback(
        script, story.get("title", ""), offer, hashtags
    )
    return {
        "script": script,
        "hashtags": hashtags,
        "youtube_metadata": youtube_meta,
        "tiktok_caption": tiktok_caption,
        "ab_test_pack": ab_test_pack,
        "source": "offline_fallback",
    }
