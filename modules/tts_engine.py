"""
edge-tts를 이용한 다국어 TTS 생성 모듈
지원 언어: ko, en, ja, zh, es, fr, de, pt, ar, hi, it, ru
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

# ── 언어별 음성 매핑 ───────────────────────────────────────────
# 전체 목록: https://docs.microsoft.com/azure/cognitive-services/speech-service/language-support
VOICE_MAP = {
    # Korean (한국어)
    ("ko", "male"):   "ko-KR-InJoonNeural",
    ("ko", "female"): "ko-KR-SunHiNeural",

    # English
    ("en", "male"):   "en-US-GuyNeural",
    ("en", "female"): "en-US-JennyNeural",

    # Japanese (日本語)
    ("ja", "male"):   "ja-JP-KeitaNeural",
    ("ja", "female"): "ja-JP-NanamiNeural",

    # Chinese Simplified (普通话)
    ("zh", "male"):   "zh-CN-YunjianNeural",
    ("zh", "female"): "zh-CN-XiaoxiaoNeural",

    # Spanish (Español)
    ("es", "male"):   "es-ES-AlvaroNeural",
    ("es", "female"): "es-ES-ElviraNeural",

    # French (Français)
    ("fr", "male"):   "fr-FR-HenriNeural",
    ("fr", "female"): "fr-FR-DeniseNeural",

    # German (Deutsch)
    ("de", "male"):   "de-DE-ConradNeural",
    ("de", "female"): "de-DE-KatjaNeural",

    # Portuguese - Brazilian (Português)
    ("pt", "male"):   "pt-BR-AntonioNeural",
    ("pt", "female"): "pt-BR-FranciscaNeural",

    # Arabic (العربية)
    ("ar", "male"):   "ar-SA-HamedNeural",
    ("ar", "female"): "ar-SA-ZariyahNeural",

    # Hindi (हिन्दी)
    ("hi", "male"):   "hi-IN-MadhurNeural",
    ("hi", "female"): "hi-IN-SwaraNeural",

    # Italian (Italiano)
    ("it", "male"):   "it-IT-DiegoNeural",
    ("it", "female"): "it-IT-ElsaNeural",

    # Russian (Русский)
    ("ru", "male"):   "ru-RU-DmitryNeural",
    ("ru", "female"): "ru-RU-SvetlanaNeural",
}

# 언어별 TTS 속도 (한/중/일/아랍어는 조금 느리게)
RATE_MAP = {
    "ko": "+10%",
    "ja": "+5%",
    "zh": "+5%",
    "ar": "+0%",
    "hi": "+5%",
}
DEFAULT_RATE = "+10%"


class TTSEngine:
    def __init__(self, lang="ko", voice="male"):
        if not EDGE_TTS_AVAILABLE:
            raise ImportError("edge-tts를 설치하세요: pip install edge-tts")
        self.lang = lang
        key = (lang, voice)
        if key in VOICE_MAP:
            self.voice_name = VOICE_MAP[key]
        else:
            # 해당 언어의 male fallback 시도
            fallback = (lang, "male")
            if fallback in VOICE_MAP:
                self.voice_name = VOICE_MAP[fallback]
                print(f"   [warn] '{voice}' voice not available for '{lang}', using male")
            else:
                # 지원 안 되는 언어는 영어로 대체
                self.voice_name = VOICE_MAP[("en", "male")]
                print(f"   [warn] Language '{lang}' not supported, using en-US fallback")

        self.rate = RATE_MAP.get(lang, DEFAULT_RATE)
        print(f"   [tts] Voice: {self.voice_name}  Rate: {self.rate}")

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
            preview = text[:70].replace("\n", " ")
            if len(text) > 70:
                preview += "..."
            print(f'   [tts] [{i+1}/{total}] "{preview}"')
            asyncio.run(self._generate(text, str(out_path)))
            paths.append(str(out_path))

        return paths

    async def _generate(self, text, output_path):
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice_name,
            rate=self.rate,
            volume="+0%",
            pitch="+0Hz",
        )
        await communicate.save(output_path)
