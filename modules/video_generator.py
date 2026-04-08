# modules/video_generator.py
import asyncio
import edge_tts
from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    VideoClip,
)
import requests
import random
import os
from dotenv import load_dotenv
from config import PEXELS_API_KEY, VIDEO_WIDTH, VIDEO_HEIGHT, FPS, AVATAR_DIR

load_dotenv()


def _elevenlabs_tts(text: str, output_path: str) -> str:
    api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "").strip()
    model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2").strip()
    if not api_key or not voice_id:
        raise ValueError("Missing ELEVENLABS_API_KEY or ELEVENLABS_VOICE_ID")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "accept": "audio/mpeg",
        "content-type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": float(os.getenv("ELEVENLABS_STABILITY", "0.5")),
            "similarity_boost": float(os.getenv("ELEVENLABS_SIMILARITY_BOOST", "0.75")),
            "style": float(os.getenv("ELEVENLABS_STYLE", "0.0")),
            "use_speaker_boost": os.getenv("ELEVENLABS_SPEAKER_BOOST", "true").lower() == "true",
        },
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(resp.content)
    return output_path

async def text_to_speech(text: str, output_path: str, voice: str = "vi-VN-HoaiMyNeural"):
    """
    ElevenLabs: chỉ khi TTS_PROVIDER=elevenlabs (hoặc 11labs) VÀ có API key + voice_id.
    Tránh gọi ElevenLabs khi để trống key → lỗi 402 spam log.
    Fallback: Edge TTS (có retry).
    """
    provider = os.getenv("TTS_PROVIDER", "").strip().lower()
    el_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    el_voice = os.getenv("ELEVENLABS_VOICE_ID", "").strip()
    use_elevenlabs = provider in {"elevenlabs", "11labs"} and el_key and el_voice

    if use_elevenlabs:
        try:
            return _elevenlabs_tts(text, output_path)
        except Exception as e:
            print(f"⚠️ ElevenLabs lỗi ({e}), chuyển sang Edge TTS...")

    voices_to_try = []
    if voice:
        voices_to_try.append(voice)
    for v in ["vi-VN-HoaiMyNeural", "vi-VN-NamMinhNeural"]:
        if v not in voices_to_try:
            voices_to_try.append(v)

    last_err = None
    for v in voices_to_try:
        for attempt in range(3):
            try:
                communicate = edge_tts.Communicate(text, v)
                await communicate.save(output_path)
                return output_path
            except Exception as e:
                last_err = e
                if attempt < 2:
                    wait = 1.5 * (attempt + 1) + random.uniform(0, 0.8)
                    print(f"⚠️ Edge TTS lỗi ({e}), thử lại sau {wait:.1f}s (voice={v})...")
                    await asyncio.sleep(wait)

    # Final fallback: generate a silent track so the pipeline can still render a video.
    try:
        import numpy as np
        from moviepy.audio.AudioClip import AudioArrayClip

        # Rough estimate: ~2.5 words/sec, clamp to 12–60s.
        word_count = max(1, len(text.split()))
        duration = max(12.0, min(60.0, word_count / 2.5))
        sr = 44100
        samples = int(duration * sr)
        silent = np.zeros((samples, 2), dtype=np.float32)
        AudioArrayClip(silent, fps=sr).write_audiofile(output_path, fps=sr, nbytes=2, bitrate="192k", logger=None)
        print(f"⚠️ EdgeTTS lỗi ({last_err}); đã tạo audio im lặng {duration:.1f}s để tiếp tục pipeline.")
        return output_path
    except Exception as e:
        raise RuntimeError(f"EdgeTTS failed and silent fallback failed: {last_err} / {e}")

def get_background_image(keyword: str = None) -> str:
    """Tải ảnh nền từ Pexels, nếu lỗi thì dùng ảnh đen"""
    if keyword is None:
        keywords = ["mysterious forest", "dark sky", "old library", "abandoned house", "foggy night"]
        keyword = random.choice(keywords)
    
    url = f"https://api.pexels.com/v1/search?query={keyword}&per_page=1"
    headers = {"Authorization": PEXELS_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('photos') and len(data['photos']) > 0:
                img_url = data['photos'][0]['src']['large2x']
                img_data = requests.get(img_url, timeout=30).content
                img_path = f"temp_bg_{random.randint(1, 10000)}.jpg"
                with open(img_path, 'wb') as f:
                    f.write(img_data)
                return img_path
    except Exception as e:
        print(f"⚠️ Lỗi lấy ảnh Pexels: {e}")
    
    # Fallback: tạo ảnh đen gradient đơn giản
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    for i in range(0, VIDEO_HEIGHT, 50):
        draw.rectangle([0, i, VIDEO_WIDTH, i+25], fill='#16213e')
    img_path = "temp_bg_fallback.jpg"
    img.save(img_path)
    return img_path

def add_subtitles(clip, text: str, duration: float) -> CompositeVideoClip:
    """Thêm phụ đề vào video (chia nhỏ câu để dễ đọc)"""
    # Chia text thành các đoạn ngắn
    sentences = text.replace('. ', '.\n').replace('? ', '?\n').replace('! ', '!\n')
    sentences = sentences.split('\n')
    
    # Tạo từng đoạn phụ đề
    subtitle_clips = []
    char_time = duration / len(text)
    current_time = 0
    
    for sentence in sentences:
        if len(sentence.strip()) < 5:
            continue
        
        sentence_duration = len(sentence) * char_time
        txt_clip = TextClip(
            text=sentence.strip(),
            font_size=45,
            color="white",
            stroke_color="black",
            stroke_width=2,
            method="caption",
            size=(VIDEO_WIDTH - 80, None),
        ).with_position(("center", VIDEO_HEIGHT - 150)).with_start(current_time).with_duration(sentence_duration)
        
        subtitle_clips.append(txt_clip)
        current_time += sentence_duration
    
    return CompositeVideoClip([clip] + subtitle_clips)

def _is_valid_image_file(path: str) -> bool:
    try:
        from PIL import Image

        with Image.open(path) as im:
            im.load()
        return True
    except Exception:
        return False


def get_avatar_path() -> str:
    """Lấy đường dẫn avatar ngẫu nhiên (bỏ qua file placeholder / không phải ảnh hợp lệ)."""
    if not os.path.isdir(AVATAR_DIR):
        return None
    names = [
        f
        for f in os.listdir(AVATAR_DIR)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    ]
    valid = [f for f in names if _is_valid_image_file(os.path.join(AVATAR_DIR, f))]
    if valid:
        return os.path.join(AVATAR_DIR, random.choice(valid))
    return None

async def create_video(script: str, output_path: str) -> str:
    """Tạo video hoàn chỉnh"""
    
    print("   🎤 Đang tạo voice...")
    voice_path = "temp_voice.mp3"
    await text_to_speech(script, voice_path)
    
    print("   🖼️ Đang lấy ảnh nền...")
    audio_clip = AudioFileClip(voice_path)
    duration = audio_clip.duration
    
    bg_img_path = get_background_image()
    bg_clip = ImageClip(bg_img_path).resized(new_size=(VIDEO_WIDTH, VIDEO_HEIGHT)).with_duration(duration)
    
    # Hiệu ứng zoom nhẹ
    def make_frame(t):
        zoom = 1 + 0.03 * (t / duration)
        frame = bg_clip.get_frame(t)
        h, w = frame.shape[:2]
        new_h, new_w = int(h * zoom), int(w * zoom)
        from skimage.transform import resize
        zoomed = resize(frame, (new_h, new_w), anti_aliasing=True)
        # Crop về đúng kích thước
        start_h = (new_h - VIDEO_HEIGHT) // 2
        start_w = (new_w - VIDEO_WIDTH) // 2
        return zoomed[start_h:start_h+VIDEO_HEIGHT, start_w:start_w+VIDEO_WIDTH]
    
    try:
        bg_zoomed = VideoClip(make_frame, duration=duration)
    except:
        bg_zoomed = bg_clip
    
    # Thêm avatar nếu có
    avatar_path = get_avatar_path()
    if avatar_path:
        print("   👤 Đang thêm avatar...")
        try:
            # Avoid imageio backend issues by loading via Pillow.
            from PIL import Image
            import numpy as np

            avatar_img = np.array(Image.open(avatar_path).convert("RGBA"))
            avatar = (
                ImageClip(avatar_img)
                .resized(height=250)
                .with_position((20, VIDEO_HEIGHT - 300))
                .with_duration(duration)
            )
            final_clip = CompositeVideoClip([bg_zoomed, avatar])
        except Exception as e:
            print(f"⚠️ Không thể load avatar ({e}), bỏ qua avatar.")
            final_clip = bg_zoomed
    else:
        final_clip = bg_zoomed
    
    music = None
    try:
        # Thêm phụ đề
        print("   📝 Đang thêm phụ đề...")
        final_clip = add_subtitles(final_clip, script, duration)

        # Thêm nhạc nền (nếu có)
        music_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "background_music", "mystery.mp3")
        if os.path.isfile(music_path) and os.path.getsize(music_path) > 512:
            try:
                music = AudioFileClip(music_path).with_volume_scaled(0.25)
                music_duration = min(duration, music.duration)
                if music_duration > 0:
                    music = music.subclipped(0, music_duration)
                    final_audio = CompositeAudioClip([audio_clip, music.with_duration(duration)])
                    final_clip = final_clip.with_audio(final_audio)
                else:
                    final_clip = final_clip.with_audio(audio_clip)
            except Exception as e:
                print(f"⚠️ Không đọc được nhạc nền ({e}), bỏ qua nhạc nền.")
                music = None
                final_clip = final_clip.with_audio(audio_clip)
        else:
            final_clip = final_clip.with_audio(audio_clip)

        # Xuất video
        print("   💾 Đang xuất video (có thể mất 1-2 phút)...")
        final_clip.write_videofile(
            output_path,
            fps=FPS,
            codec='libx264',
            audio_codec='aac',
            threads=4,
            preset="ultrafast",
            logger="bar",
        )
        return output_path
    finally:
        # Dọn dẹp tài nguyên
        for clip in [music, audio_clip, bg_clip, final_clip]:
            try:
                if clip is not None:
                    clip.close()
            except Exception:
                pass
        for f in [voice_path, bg_img_path]:
            if os.path.exists(f):
                os.remove(f)