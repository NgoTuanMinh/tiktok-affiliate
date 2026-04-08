# modules/seo_generator.py
import google.generativeai as genai
import json
from config import GEMINI_API_KEY, DEFAULT_HASHTAGS

genai.configure(api_key=GEMINI_API_KEY)
# Use a currently-available model name (see `genai.list_models()`).
model = genai.GenerativeModel("gemini-2.0-flash")

def generate_hashtags(script: str, title: str) -> str:
    """Sinh 20-30 hashtags từ kịch bản"""
    prompt = f"""
Dựa trên nội dung sau, hãy tạo 20-30 hashtags cho video TikTok:

TIÊU ĐỀ: {title}
NỘI DUNG KỊCH BẢN: {script[:500]}

YÊU CẦU HASHTAGS:
- 5 hashtags trending: #fyp #xuhuong #viral #tiktokvietnam #shorts
- 10 hashtags chủ đề: liên quan đến bí ẩn, tâm lý học, câu chuyện
- 5 hashtags cảm xúc: #soc #tam_su #hoc_duong #kham_pha #bi_an
- 5 hashtags hành động: #theo_doi #comment #chia_se

Trả về dạng text, mỗi hashtag cách nhau 1 space, bắt đầu bằng #.
Ví dụ: #fyp #xuhuong #bi_an #tam_ly_hoc
"""

    try:
        response = model.generate_content(prompt)
        hashtags = response.text.strip()
        if len(hashtags.split()) < 15:
            hashtags += " " + DEFAULT_HASHTAGS
        return hashtags
    except:
        return DEFAULT_HASHTAGS


def generate_affiliate_caption(script: str, title: str, offer: dict) -> str:
    """Sinh caption TikTok tối ưu affiliate conversion theo offer."""
    offer_name = offer.get("name", "tài nguyên liên quan")
    benefit = offer.get("benefit", "")
    cta_hint = offer.get("cta_hint", "Mình để link ở bio/giỏ hàng, bấm vào xem nhé.")
    affiliate_link = offer.get("affiliate_link", "[DAN_LINK_AFFILIATE_VAO_DAY]")

    prompt = f"""
Tạo caption TikTok bằng tiếng Việt, ngách faceless storytelling + tâm lý học.

TIÊU ĐỀ VIDEO: {title}
KỊCH BẢN: {script[:500]}
OFFER: {offer_name}
BENEFIT: {benefit}
CTA: {cta_hint}
LINK: {affiliate_link}

YÊU CẦU:
- Viết caption ngắn 450-650 ký tự, dễ đọc.
- Có hook 1 câu đầu mạnh.
- Chèn lợi ích của offer tự nhiên trong mạch kể chuyện.
- Có CTA rõ ràng bấm link.
- Không nói quá đà, không cam kết phi thực tế.
- Cuối caption có block hashtags 10-18 hashtag.

Trả về text thuần, không markdown.
"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "#" not in text:
            text += f"\n\n{DEFAULT_HASHTAGS}"
        return text
    except:
        return (
            f"{title}\n\n"
            f"Nếu bạn từng thấy mình trong câu chuyện này, thử {offer_name} để {benefit}. "
            f"{cta_hint}\n"
            f"Link: {affiliate_link}\n\n"
            f"{DEFAULT_HASHTAGS}"
        )


def generate_ab_test_pack(script: str, title: str, offer: dict, hashtags: str) -> dict:
    """
    Tạo bộ A/B test để đăng tay:
    - 3 hook variants
    - 3 caption variants
    - 3 pinned comment CTA variants
    """
    offer_name = offer.get("name", "tài nguyên liên quan")
    cta_hint = offer.get("cta_hint", "Mình để link ở bio/giỏ hàng, bấm vào xem nhé.")
    affiliate_link = offer.get("affiliate_link", "[DAN_LINK_AFFILIATE_VAO_DAY]")

    prompt = f"""
Bạn là chuyên gia TikTok affiliate.
Hãy tạo bộ A/B test cho video ngách bí ẩn + tâm lý học.

Tiêu đề: {title}
Kịch bản: {script[:700]}
Offer: {offer_name}
CTA: {cta_hint}
Link: {affiliate_link}
Hashtags: {hashtags}

Yêu cầu xuất JSON đúng định dạng:
{{
  "hook_variants": ["...", "...", "..."],
  "caption_variants": ["...", "...", "..."],
  "pinned_comment_variants": ["...", "...", "..."]
}}

Quy tắc:
- Hook ngắn, tò mò, không giật gân quá mức.
- Caption ưu tiên conversion mềm, không cam kết phi thực tế.
- Comment ghim phải có CTA bấm link tự nhiên.
- Giữ tiếng Việt tự nhiên.
"""
    try:
        response = model.generate_content(prompt)
        text = response.text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            data = json.loads(text[start:end])
            for key in ["hook_variants", "caption_variants", "pinned_comment_variants"]:
                if key not in data or not isinstance(data[key], list):
                    raise ValueError(f"Missing key: {key}")
                data[key] = [str(x).strip() for x in data[key][:3] if str(x).strip()]
            return data
    except Exception:
        pass

    # Fallback đơn giản để đảm bảo luôn có pack A/B test
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
        "Ai muốn mình tổng hợp thêm tài nguyên cùng chủ đề thì comment \"link\".",
        f"Bạn có thể xem thử trước ở đây: {affiliate_link}",
    ]
    return {
        "hook_variants": hooks,
        "caption_variants": captions,
        "pinned_comment_variants": comments,
    }

def generate_youtube_metadata(title: str, script: str) -> dict:
    """Sinh title và description cho YouTube Shorts"""
    prompt = f"""
Tạo metadata cho YouTube Shorts với nội dung:
TIÊU ĐỀ GỐC: {title}
KỊCH BẢN: {script[:300]}

Trả về JSON duy nhất:
{{
    "title": "tiêu đề dưới 60 ký tự, hấp dẫn, có từ khóa",
    "description": "mô tả 150-200 ký tự, tóm tắt nội dung, kèm CTA và hashtags #shorts #storytime"
}}
"""

    try:
        response = model.generate_content(prompt)
        # Lấy phần JSON từ response
        text = response.text
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            return json.loads(text[start:end])
    except:
        pass
    
    return {
        "title": title[:55] + " #shorts",
        "description": script[:180] + "\n\n#storytime #bi_an #shorts"
    }