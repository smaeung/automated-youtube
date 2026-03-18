"""
moviepy: slides + audio -> MP4 (자막 오버레이 포함)
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
from PIL import Image

try:
    from moviepy.editor import (
        ImageClip,
        AudioFileClip,
        concatenate_videoclips,
    )
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False


class VideoBuilder:
    FPS = 30

    def __init__(self):
        if not MOVIEPY_AVAILABLE:
            raise ImportError(
                "moviepy를 설치하세요: pip install 'moviepy>=1.0.3,<2.0.0'"
            )

    def build(self, slide_paths, audio_paths, output_path, script=None):
        """
        슬라이드 이미지 + TTS 음성 → 자막 포함 MP4 영상.
        script가 있으면 각 슬라이드 나레이션을 자막으로 오버레이.
        """
        from modules.slide_maker import SlideMaker

        if len(slide_paths) != len(audio_paths):
            n = min(len(slide_paths), len(audio_paths))
            print(f"   [warn] slides({len(slide_paths)}) != audio({len(audio_paths)}) -> using {n}")
            slide_paths = slide_paths[:n]
            audio_paths = audio_paths[:n]

        slides_data = (script or {}).get("slides", [])
        sub_maker = SlideMaker(output_dir=".")   # 폰트·자막 렌더링용

        final_clips = []
        total = len(slide_paths)

        for i, (img_path, audio_path) in enumerate(zip(slide_paths, audio_paths)):
            print(f"   [clip] [{i+1}/{total}] 자막 합성 중...")

            audio = AudioFileClip(audio_path)
            duration = audio.duration

            slide_data = slides_data[i] if i < len(slides_data) else {}
            script_text = slide_data.get("script", "").strip()

            # 슬라이드 기본 이미지 로드 (numpy array)
            base = np.array(Image.open(img_path).convert("RGB"))

            if script_text:
                chunks = sub_maker.split_subtitle_chunks(script_text, duration)
                sub_clips = []
                for chunk_text, chunk_dur in chunks:
                    frame = sub_maker.render_subtitle_frame(base, chunk_text)
                    sub_clips.append(ImageClip(frame).set_duration(chunk_dur))
                slide_visual = concatenate_videoclips(sub_clips, method="compose")
            else:
                slide_visual = ImageClip(base).set_duration(duration)

            slide_clip = slide_visual.set_audio(audio)
            final_clips.append(slide_clip)

        print(f"\n   [render] 최종 영상 렌더링 중... (잠시 기다려주세요)")
        final = concatenate_videoclips(final_clips, method="compose")
        final.write_videofile(
            output_path,
            fps=self.FPS,
            codec="libx264",
            audio_codec="aac",
            audio_bitrate="192k",
            bitrate="4000k",
            threads=4,
            verbose=False,
            logger=None,
        )

        for clip in final_clips:
            clip.close()
        final.close()

        return output_path
