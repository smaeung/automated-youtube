"""
Multilingual TTS generation module using edge-tts.
Supported languages: ko, en, ja, zh, es, fr, de, pt, ar, hi, it, ru
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

# ── Voice map by (language, gender) ───────────────────────────
# Full list: https://docs.microsoft.com/azure/cognitive-services/speech-service/language-support
VOICE_MAP = {
    # Korean
    ("ko", "male"):   "ko-KR-InJoonNeural",
    ("ko", "female"): "ko-KR-SunHiNeural",

    # English
    ("en", "male"):   "en-US-GuyNeural",
    ("en", "female"): "en-US-JennyNeural",

    # Japanese
    ("ja", "male"):   "ja-JP-KeitaNeural",
    ("ja", "female"): "ja-JP-NanamiNeural",

    # Chinese Simplified
    ("zh", "male"):   "zh-CN-YunjianNeural",
    ("zh", "female"): "zh-CN-XiaoxiaoNeural",

    # Spanish
    ("es", "male"):   "es-ES-AlvaroNeural",
    ("es", "female"): "es-ES-ElviraNeural",

    # French
    ("fr", "male"):   "fr-FR-HenriNeural",
    ("fr", "female"): "fr-FR-DeniseNeural",

    # German
    ("de", "male"):   "de-DE-ConradNeural",
    ("de", "female"): "de-DE-KatjaNeural",

    # Portuguese (Brazil)
    ("pt", "male"):   "pt-BR-AntonioNeural",
    ("pt", "female"): "pt-BR-FranciscaNeural",

    # Arabic
    ("ar", "male"):   "ar-SA-HamedNeural",
    ("ar", "female"): "ar-SA-ZariyahNeural",

    # Hindi
    ("hi", "male"):   "hi-IN-MadhurNeural",
    ("hi", "female"): "hi-IN-SwaraNeural",

    # Italian
    ("it", "male"):   "it-IT-DiegoNeural",
    ("it", "female"): "it-IT-ElsaNeural",

    # Russian
    ("ru", "male"):   "ru-RU-DmitryNeural",
    ("ru", "female"): "ru-RU-SvetlanaNeural",
}

# TTS speaking rate per language (CJK/Arabic slightly slower for clarity)
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
            raise ImportError("edge-tts is not installed: pip install edge-tts")
        self.lang = lang
        key = (lang, voice)
        if key in VOICE_MAP:
            self.voice_name = VOICE_MAP[key]
        else:
            # Fallback to male voice for the same language
            fallback = (lang, "male")
            if fallback in VOICE_MAP:
                self.voice_name = VOICE_MAP[fallback]
                print(f"   [warn] '{voice}' voice not available for '{lang}', using male")
            else:
                # Unsupported language: fall back to English
                self.voice_name = VOICE_MAP[("en", "male")]
                print(f"   [warn] Language '{lang}' not supported, using en-US fallback")

        self.rate = RATE_MAP.get(lang, DEFAULT_RATE)
        print(f"   [tts] Voice: {self.voice_name}  Rate: {self.rate}")

    def generate_all(self, script, output_dir):
        """Generate MP3 files for every slide script in the JSON."""
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
