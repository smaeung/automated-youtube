#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
"""
🎬 Auto YouTube Shorts Video Creator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
주제를 입력하거나, 자동으로 트렌드를 탐색해 YouTube Shorts 영상을 제작합니다.

사용법:
  python auto_video.py                           # 자동 트렌드 탐색 후 영상 제작
  python auto_video.py --topic "GTC 2026"        # 주제 직접 지정
  python auto_video.py --list-trends             # 현재 트렌드 목록만 출력
  python auto_video.py --topic "AI" --no-video   # 스크립트만 생성 (영상 제작 X)
  python auto_video.py --voice female            # 여성 TTS 목소리
  python auto_video.py --slides 6               # 슬라이드 6개
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def parse_args():
    p = argparse.ArgumentParser(
        description="🎬 자동 유튜브 쇼츠 영상 제작기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--topic",      type=str, help="영상 주제 (미입력 시 자동 탐색)")
    p.add_argument("--slides",     type=int, default=8, help="슬라이드 수 (기본: 8)")
    p.add_argument("--duration",   type=str, default="5min",
                   choices=["1min", "3min", "5min", "10min"], help="영상 길이 (기본: 5min)")
    p.add_argument("--voice",      type=str, default="male",
                   choices=["male", "female"], help="TTS 목소리 (기본: male)")
    p.add_argument("--lang",       type=str, default="ko",
                   choices=["ko", "en"], help="언어 (기본: ko)")
    p.add_argument("--output",     type=str, default="output", help="출력 디렉토리")
    p.add_argument("--list-trends", action="store_true", help="트렌드 목록만 출력")
    p.add_argument("--no-video",   action="store_true", help="스크립트만 생성 (영상 X)")
    return p.parse_args()


def banner():
    print()
    print("┌─────────────────────────────────────────────┐")
    print("│  🎬  Auto YouTube Shorts Video Creator      │")
    print("│      powered by Claude + edge-tts + PIL     │")
    print("└─────────────────────────────────────────────┘")
    print()


def step(n, total, label):
    print(f"\n[{n}/{total}] {label}")
    print("─" * 48)


def main():
    args = parse_args()
    banner()

    # ── 출력 디렉토리 ────────────────────────────────────────
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    TOTAL_STEPS = 6 if not args.no_video else 2

    # ── STEP 1: 트렌드 탐색 ─────────────────────────────────
    step(1, TOTAL_STEPS, "트렌드 탐색")
    from modules.trend_finder import TrendFinder
    finder = TrendFinder(lang=args.lang)

    if args.list_trends:
        trends = finder.get_trends(limit=10)
        print("\n📊 현재 트렌드 TOP 10:\n")
        for i, t in enumerate(trends, 1):
            print(f"  {i:2d}. {t['topic']}")
            print(f"      → {t['reason']}")
        print()
        return

    if args.topic:
        topic_info = {
            "topic": args.topic,
            "reason": "사용자 직접 지정",
            "description": "",
        }
        print(f"✅ 주제: {args.topic}")
    else:
        print("🔍 트렌드 탐색 중...")
        trends = finder.get_trends(limit=5)
        topic_info = trends[0]
        print(f"📈 선택된 트렌드: {topic_info['topic']}")
        print(f"   이유: {topic_info['reason']}")

    topic = topic_info["topic"]

    # ── STEP 2: 스크립트 생성 ───────────────────────────────
    step(2, TOTAL_STEPS, f"스크립트 생성 (Claude {args.slides}슬라이드)")
    from modules.script_gen import ScriptGenerator
    try:
        gen = ScriptGenerator(lang=args.lang)
    except ValueError as e:
        print(f"\n❌ {e}")
        sys.exit(1)

    script = gen.generate(
        topic=topic,
        topic_info=topic_info,
        num_slides=args.slides,
        duration=args.duration,
    )

    script_path = out_dir / f"script_{timestamp}.json"
    script_path.write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 스크립트 저장: {script_path}")
    print(f"📋 YouTube 제목: {script.get('youtube_title', '(없음)')}")

    if args.no_video:
        print("\n✅ 스크립트 생성 완료 (--no-video 모드)")
        _print_meta(script)
        return

    # ── STEP 3: 배경 이미지 검색 ────────────────────────────
    step(3, TOTAL_STEPS, "배경 이미지 검색 (DuckDuckGo)")
    from modules.image_search import ImageSearcher
    searcher = ImageSearcher()
    images_dir = out_dir / f"images_{timestamp}"
    if searcher.available:
        images_dir.mkdir(exist_ok=True)
        print(f"   이미지 다운로드 준비 완료 → {images_dir}")
    else:
        print("   [skip] duckduckgo-search 미설치 — 기본 배경 사용")
        print("   설치: pip install duckduckgo-search")
        searcher = None

    # ── STEP 4: 슬라이드 이미지 생성 ───────────────────────
    step(4, TOTAL_STEPS, "슬라이드 이미지 생성 (PIL + 웹 배경)")
    from modules.slide_maker import SlideMaker
    slide_dir = out_dir / f"slides_{timestamp}"
    slide_dir.mkdir(exist_ok=True)
    maker = SlideMaker(
        output_dir=slide_dir,
        searcher=searcher,
        images_dir=images_dir if searcher else None,
    )
    slide_paths = maker.create_all(script)
    print(f"✅ {len(slide_paths)}개 슬라이드 생성 완료")

    # ── STEP 5: TTS 음성 생성 ───────────────────────────────
    step(5, TOTAL_STEPS, f"TTS 음성 생성 (edge-tts / {args.voice})")
    from modules.tts_engine import TTSEngine
    audio_dir = out_dir / f"audio_{timestamp}"
    audio_dir.mkdir(exist_ok=True)
    tts = TTSEngine(lang=args.lang, voice=args.voice)
    audio_paths = tts.generate_all(script, output_dir=audio_dir)
    print(f"✅ {len(audio_paths)}개 음성 파일 생성 완료")

    # ── STEP 6: 영상 조립 + 자막 ────────────────────────────
    step(6, TOTAL_STEPS, "영상 조립 + 자막 합성 (moviepy)")
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
    print("│  ✅  영상 제작 완료!                         │")
    print("└─────────────────────────────────────────────┘")
    print(f"  📁 파일  : {final_path}")
    _print_meta(script)


def _print_meta(script):
    print()
    print("📋 YouTube 메타데이터:")
    print(f"  제목  : {script.get('youtube_title', 'N/A')}")
    tags = " ".join(script.get("hashtags", [])[:5])
    print(f"  태그  : {tags}")
    desc = script.get("description", "")
    if desc:
        print(f"  설명  : {desc[:80]}{'...' if len(desc) > 80 else ''}")
    print()


if __name__ == "__main__":
    main()
