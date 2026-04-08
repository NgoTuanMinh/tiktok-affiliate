# modules/script_generator.py
import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
# Use a currently-available model name (see `genai.list_models()`).
model = genai.GenerativeModel("gemini-2.0-flash")

STORYTELLING_PROMPT = """
Bạn là một người kể chuyện chuyên nghiệp trên TikTok, có giọng kể cuốn hút và bí ẩn.

Hãy viết kịch bản video 30-45 giây dựa trên nội dung sau:

TIÊU ĐỀ: {title}
NỘI DUNG: {content}

YÊU CẦU KỊCH BẢN:
1. HOOK (3-5 giây đầu): Một câu hỏi hoặc câu nói gây sốc, tò mò. Ví dụ: "Bạn có tin rằng có người không cần ngủ trong 40 năm?"

2. THÂN BÀI (20-30 giây): Kể câu chuyện với nhịp độ nhanh, thêm chi tiết gây tò mò, có thể đặt câu hỏi tu từ.

3. KẾT THÚC (5 giây cuối): CTA (Call-to-Action) mềm mại. Ví dụ: "Theo dõi mình để nghe thêm nhiều câu chuyện bí ẩn nhé!" hoặc "Comment suy nghĩ của bạn về câu chuyện này!"

QUY TẮC VIẾT:
- Giọng văn tự nhiên, như đang nói chuyện
- Câu ngắn, dễ đọc
- Có thể dùng câu hỏi để tương tác
- Độ dài: 180-250 từ

CHỈ TRẢ VỀ KỊCH BẢN, KHÔNG THÊM GIẢI THÍCH.
"""

def generate_script(story: dict, offer: dict = None) -> str:
    """Sinh kịch bản từ câu chuyện + chèn CTA affiliate theo offer"""
    prompt = STORYTELLING_PROMPT.format(
        title=story.get('title', 'Câu chuyện bí ẩn'),
        content=story.get('content', '')
    )

    if offer:
        prompt += f"""

NGỮ CẢNH KIẾM TIỀN AFFILIATE:
- Offer: {offer.get('name', '')}
- Pain point: {offer.get('pain_point', '')}
- Benefit: {offer.get('benefit', '')}
- CTA gợi ý: {offer.get('cta_hint', '')}

YÊU CẦU THÊM:
- Kết thúc bằng CTA tự nhiên, hướng người xem bấm link ở bio/giỏ hàng/mô tả.
- Không bán hàng lộ liễu; giữ tone kể chuyện bí ẩn + tâm lý học.
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"⚠️ Lỗi sinh kịch bản: {e}")
        # Fallback script
        cta = offer.get("cta_hint", "Mình để link tài nguyên liên quan ở bio nhé!") if offer else "Mình để link tài nguyên liên quan ở bio nhé!"
        return f"""Bạn có biết? {story.get('title', 'Câu chuyện này')} 
        
{story.get('content', '')[:200]}

Điều này khiến nhiều người bất ngờ đấy! {cta} #bi_an #xuhuong"""