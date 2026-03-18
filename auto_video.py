#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
"""
Auto YouTube Shorts Video Creator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Automatically finds trending topics and creates YouTube Shorts videos.
Supports 12 languages via --lang option.

Usage:
  python auto_video.py                              # Auto trend + Korean video
  python auto_video.py --topic "GTC 2026"           # Set topic manually
  python auto_video.py --list-trends                # Show trend list only
  python auto_video.py --topic "AI" --no-video      # Script only (no video)
  python auto_video.py --voice female               # Female TTS voice
  python auto_video.py --slides 6                   # 6 slides
  python auto_video.py --lang en                    # English
  python auto_video.py --lang ja                    # Japanese
  python auto_video.py --lang zh                    # Chinese
  python auto_video.py --lang es                    # Spanish
  python auto_video.py --lang fr                    # French
  python auto_video.py --lang de                    # German
  python auto_video.py --lang pt                    # Portuguese (Brazil)
  python auto_video.py --lang ar                    # Arabic
  python auto_video.py --lang hi                    # Hindi
  python auto_video.py --lang it                    # Italian
  python auto_video.py --lang ru                    # Russian
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# 지원 언어 목록
SUPPORTED_LANGS = ["ko", "en", "ja", "zh", "es", "fr", "de", "pt", "ar", "hi", "it", "ru"]

LANG_LABEL = {
    "ko": "Korean (한국어)",
    "en": "English",
    "ja": "Japanese (日本語)",
    "zh": "Chinese (中文)",
    "es": "Spanish (Español)",
    "fr": "French (Français)",
    "de": "German (Deutsch)",
    "pt": "Portuguese (Português)",
    "ar": "Arabic (العربية)",
    "hi": "Hindi (हिन्दी)",
    "it": "Italian (Italiano)",
    "ru": "Russian (Русский)",
}


def parse_args():
    p = argparse.ArgumentParser(
        description="Auto YouTube Shorts Video Creator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--topic",      type=str, help="Video topic (auto-detected if not set)")
    p.add_argument("--slides",     type=int, default=8, help="Number of slides (default: 8)")
    p.add_argument("--duration",   type=str, default="5min",
                   choices=["1min", "3min", "5min", "10min"], help="Video length (default: 5min)")
    p.add_argument("--voice",      type=str, default="male",
                   choices=["male", "female"], help="TTS voice gender (default: male)")
    p.add_argument("--lang",       type=str, default="ko",
                   choices=SUPPORTED_LANGS,
                   help=f"Output language (default: ko). Supported: {', '.join(SUPPORTED_LANGS)}")
    p.add_argument("--output",     type=str, default="output", help="Output directory")
    p.add_argument("--list-trends", action="store_true", help="Show trend list and exit")
    p.add_argument("--no-video",   action="store_true", help="Generate script only (no video)")
    return p.parse_args()


def banner(lang="ko"):
    label = LANG_LABEL.get(lang, lang)
    print()
    print("┌─────────────────────────────────────────────┐")
    print("│  Auto YouTube Shorts Video Creator          │")
    print("│  powered by Claude + edge-tts + PIL         │")
    print(f"│  Language: {label:<33}│")
    print("└─────────────────────────────────────────────┘")
    print()


def step(n, total, label):
    print(f"\n[{n}/{total}] {label}")
    print("─" * 48)


def main():
    args = parse_args()
    banner(args.lang)

    # ── 출력 디렉토리 ────────────────────────────────────────
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    TOTAL_STEPS = 6 if not args.no_video else 2

    # ── STEP 1: 트렌드 탐색 ─────────────────────────────────
    step(1, TOTAL_STEPS, f"Trend Search [{LANG_LABEL.get(args.lang, args.lang)}]")
    from modules.trend_finder import TrendFinder
    finder = TrendFinder(lang=args.lang)

    if args.list_trends:
        trends = finder.get_trends(limit=10)
        print(f"\n  Top 10 Trends [{LANG_LABEL.get(args.lang, args.lang)}]:\n")
        for i, t in enumerate(trends, 1):
            print(f"  {i:2d}. {t['topic']}")
            print(f"      => {t['reason']}")
        print()
        return

    if args.topic:
        topic_info = {
            "topic": args.topic,
            "reason": "User specified",
            "description": "",
        }
        print(f"   Topic: {args.topic}")
    else:
        print("   Searching trends...")
        trends = finder.get_trends(limit=5)
        topic_info = trends[0]
        print(f"   Selected: {topic_info['topic']}")
        print(f"   Reason  : {topic_info['reason']}")

    topic = topic_info["topic"]

    # ── STEP 2: 스크립트 생성 ───────────────────────────────
    step(2, TOTAL_STEPS, f"Script Generation (Claude, {args.slides} slides, {args.lang})")
    from modules.script_gen import ScriptGenerator
    try:
        gen = ScriptGenerator(lang=args.lang)
    except ValueError as e:
        print(f"\n  ERROR: {e}")
        sys.exit(1)

    script = gen.generate(
        topic=topic,
        topic_info=topic_info,
        num_slides=args.slides,
        duration=args.duration,
    )

    script_path = out_dir / f"script_{timestamp}.json"
    script_path.write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"   Saved  : {script_path}")
    print(f"   Title  : {script.get('youtube_title', '(none)')}")

    if args.no_video:
        print("\n   Script generated (--no-video mode)")
        _print_meta(script)
        return

    # ── STEP 3: 배경 이미지 검색 ────────────────────────────
    step(3, TOTAL_STEPS, "Background Image Search (DuckDuckGo)")
    from modules.image_search import ImageSearcher
    searcher = ImageSearcher()
    images_dir = out_dir / f"images_{timestamp}"
    if searcher.available:
        images_dir.mkdir(exist_ok=True)
        print(f"   Image download ready -> {images_dir}")
    else:
        print("   [skip] duckduckgo-search not installed — using gradient background")
        print("   Install: pip install duckduckgo-search")
        searcher = None

    # ── STEP 4: 슬라이드 이미지 생성 ───────────────────────
    step(4, TOTAL_STEPS, f"Slide Image Generation (PIL 1080x1920, {args.lang})")
    from modules.slide_maker import SlideMaker
    slide_dir = out_dir / f"slides_{timestamp}"
    slide_dir.mkdir(exist_ok=True)
    maker = SlideMaker(
        output_dir=slide_dir,
        searcher=searcher,
        images_dir=images_dir if searcher else None,
        lang=args.lang,
    )
    slide_paths = maker.create_all(script)
    print(f"   {len(slide_paths)} slides created")

    # ── STEP 5: TTS 음성 생성 ───────────────────────────────
    step(5, TOTAL_STEPS, f"TTS Audio Generation (edge-tts, {args.lang}, {args.voice})")
    from modules.tts_engine import TTSEngine
    audio_dir = out_dir / f"audio_{timestamp}"
    audio_dir.mkdir(exist_ok=True)
    tts = TTSEngine(lang=args.lang, voice=args.voice)
    audio_paths = tts.generate_all(script, output_dir=audio_dir)
    print(f"   {len(audio_paths)} audio files created")

    # ── STEP 6: 영상 조립 + 자막 ────────────────────────────
    step(6, TOTAL_STEPS, "Video Assembly + Subtitle Overlay (moviepy)")
    from modules.video_builder import VideoBuilder
    safe = "".join(c if c.isalnum() or c in " _" else "_" for c in topic).strip()[:28]
    video_path = out_dir / f"{safe}_{timestamp}.mp4"
    builder = VideoBuilder()
    final_path = builder.build(
        slide_paths=slide_paths,
        audio_paths=audio_paths,
        output_path=str(video_path),
        script=script,
    )

    # ── 완료 ────────────────────────────────────────────────
    print()
    print("┌─────────────────────────────────────────────┐")
    print("│  Video creation complete!                   │")
    print("└─────────────────────────────────────────────┘")
    print(f"  File : {final_path}")
    _print_meta(script)


def _print_meta(script):
    print()
    print("  YouTube Metadata:")
    print(f"    Title      : {script.get('youtube_title', 'N/A')}")
    tags = " ".join(script.get("hashtags", [])[:5])
    print(f"    Hashtags   : {tags}")
    desc = script.get("description", "")
    if desc:
        print(f"    Description: {desc[:80]}{'...' if len(desc) > 80 else ''}")
    print()


if __name__ == "__main__":
    main()
