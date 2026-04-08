# modules/scraper.py
import requests
import random
import time
from typing import List, Dict

class StoryScraper:
    """Lấy ý tưởng câu chuyện từ nhiều nguồn"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def get_reddit_stories(self, limit: int = 3) -> List[Dict]:
        """Lấy câu chuyện từ Reddit (không cần API key)"""
        url = "https://www.reddit.com/r/nosleep/top.json?t=week&limit=10"
        
        try:
            response = self.session.get(url, timeout=30)
            data = response.json()
            
            stories = []
            for post in data['data']['children'][:limit]:
                stories.append({
                    "title": post['data']['title'],
                    "content": post['data']['selftext'][:800],
                    "url": f"https://reddit.com{post['data']['permalink']}",
                    "score": post['data']['score'],
                    "source": "reddit"
                })
            return stories
        except Exception as e:
            print(f"⚠️ Lỗi scrape Reddit: {e}")
            return self._get_fallback_stories()
    
    def _get_fallback_stories(self) -> List[Dict]:
        """Fallback: danh sách câu chuyện mẫu (khi không có internet)"""
        return [
            {
                "title": "Người đàn ông không bao giờ ngủ",
                "content": "Một người đàn ông ở Thụy Sĩ tuyên bố mình đã không ngủ trong 40 năm qua. Các bác sĩ không thể giải thích hiện tượng này. Ông vẫn khỏe mạnh, minh mẫn và làm việc bình thường. Nghiên cứu mới nhất cho thấy có thể liên quan đến một đột biến gen hiếm gặp.",
                "source": "fallback"
            },
            {
                "title": "Bí ẩn ngôi làng không ai già đi",
                "content": "Tại một ngôi làng hẻo lánh ở Nhật Bản, các cư dân dường như không hề già đi theo thời gian. Nghiên cứu cho thấy tỷ lệ lão hóa của họ chậm hơn 30% so với trung bình thế giới. Bí mật nằm ở chế độ ăn uống và nguồn nước đặc biệt?",
                "source": "fallback"
            },
            {
                "title": "Hiệu ứng Mandela: Bạn có nhớ sai quá khứ?",
                "content": "Hàng ngàn người nhớ rằng Nelson Mandela đã chết trong tù vào những năm 1980. Nhưng sự thật ông mất năm 2013. Hiện tượng này được gọi là 'Hiệu ứng Mandela' - một tập thể cùng nhớ sai một sự kiện lịch sử. Tại sao điều này xảy ra?",
                "source": "fallback"
            }
        ]
    
    def get_random_story(self) -> Dict:
        """Lấy một câu chuyện ngẫu nhiên"""
        stories = self.get_reddit_stories(limit=5)
        if stories:
            return random.choice(stories)
        return random.choice(self._get_fallback_stories())