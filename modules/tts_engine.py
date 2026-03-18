"""
edge-tts를 이용한 한국어/영어 TTS 생성 모듈
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import asyncio
from pathlib import Path

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

VOICE_MAP = {
    ("ko", "male"):   "ko-KR-InJoonNeural",
    ("ko", "female"): "ko-KR-SunHiNeural",
    ("en", "male"):   "en-US-GuyNeural",
    ("en", "female"): "en-US-JennyNeural",
}


class TTSEngine:
    def __init__(self, lang="ko", voice="male"):
        if not EDGE_TTS_AVAILABLE:
            raise ImportError("edge-tts를 설치하세요: pip install edge-tts")
        self.voice_name = VOICE_MAP.get((lang, voice), "ko-KR-InJoonNeural")

    def generate_all(self, script, output_dir):
        """모든 슬라이드 script → MP3 파일 생성"""
        slides = script.get("slides", [])
        paths = []
        total = len(slides)

        for i, slide in enumerate(slides):
            text = slide.get("script", "").strip()
            if not text:
                continue
            out_path = Path(output_dir) / f"audio_{i+1:02d}.mp3"
            # 생성할 텍스트 미리보기 출력
            preview = text[:70].replace("\n", " ")
            if len(text) > 70:
                preview += "..."
            print(f"   [tts] [{i+1}/{total}] \"{preview}\"")
            asyncio.run(self._generate(text, str(out_path)))
            paths.append(str(out_path))

        return paths

    async def _generate(self, text, output_path):
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice_name,
            rate="+10%",    # 약간 빠르게 (유튜브 콘텐츠 적합)
            volume="+0%",
            pitch="+0Hz",
        )
        await communicate.save(output_path)
