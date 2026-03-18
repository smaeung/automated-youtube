"""
PIL/Pillow를 이용한 슬라이드 이미지 생성 모듈
해상도: 1080x1920 (9:16 YouTube Shorts)
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── 색상 팔레트 ──────────────────────────────────────────────
C = {
    "bg":         (8,   8,   8),
    "green":      (118, 185,  0),
    "green_dim":  ( 50,  80,  0),
    "green_glow": ( 20,  45,  5),
    "white":      (255, 255, 255),
    "silver":     (180, 180, 180),
    "script_bg":  ( 12,  20,  6),
    "card_bg":    ( 16,  28,  8),
    "border":     ( 35,  60, 15),
}

# 폰트 후보 경로 (Windows → Linux → macOS)
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\malgunbd.ttf",
    r"C:\Windows\Fonts\malgun.ttf",
    r"C:\Windows\Fonts\gulim.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
]


def _find_font():
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


class SlideMaker:
    W = 1080
    H = 1920

    def __init__(self, output_dir, searcher=None, images_dir=None):
        self.output_dir = Path(output_dir)
        self.searcher = searcher        # ImageSearcher 인스턴스 (없으면 배경 이미지 없이 진행)
        self.images_dir = Path(images_dir) if images_dir else None
        self.font_path = _find_font()
        self.fonts = self._load_fonts()

    # ── 폰트 로드 ───────────────────────────────────────────
    def _load_fonts(self):
        sizes = {
            "huge":   96,
            "title":  76,
            "large":  58,
            "medium": 44,
            "normal": 36,
            "small":  30,
            "tiny":   24,
            "micro":  20,
        }
        fonts = {}
        for name, size in sizes.items():
            try:
                if self.font_path:
                    fonts[name] = ImageFont.truetype(self.font_path, size, index=0)
                else:
                    fonts[name] = ImageFont.load_default()
            except Exception:
                fonts[name] = ImageFont.load_default()
        return fonts

    # ── 전체 슬라이드 생성 ──────────────────────────────────
    def create_all(self, script):
        slides = script.get("slides", [])
        topic = script.get("topic", "")
        paths = []
        total = len(slides)

        for i, slide_data in enumerate(slides):
            # 배경 이미지 검색 (searcher가 있을 때)
            bg_image_path = None
            if self.searcher and self.images_dir:
                self.images_dir.mkdir(parents=True, exist_ok=True)
                query = f"{slide_data.get('headline', '')} {topic}"
                img_out = str(self.images_dir / f"bg_{i+1:02d}.jpg")
                bg_image_path = self.searcher.search(query, img_out)
                status = "이미지 다운로드" if bg_image_path else "기본 배경"
                print(f"   [img] [{i+1}/{total}] {slide_data.get('section', '')} — {status}")
            else:
                print(f"   [img] [{i+1}/{total}] {slide_data.get('section', '')} done")

            path = self.output_dir / f"slide_{i+1:02d}.png"
            self.create_slide(slide_data, i + 1, total, str(path), bg_image_path=bg_image_path)
            paths.append(str(path))

        return paths

    # ── 단일 슬라이드 생성 ──────────────────────────────────
    def create_slide(self, data, slide_num, total_slides, output_path, bg_image_path=None):
        W, H = self.W, self.H

        # 배경: 이미지 있으면 사용, 없으면 그라디언트
        if bg_image_path:
            img = self._make_image_bg(bg_image_path)
        else:
            bg = np.full((H, W, 3), C["bg"], dtype=np.uint8)
            for y in range(500):
                ratio = (1 - y / 500) ** 2
                bg[y, :, 1] = np.clip(C["bg"][1] + int(50 * ratio), 0, 255)
                bg[y, :, 0] = np.clip(C["bg"][0] + int(10 * ratio), 0, 255)
            for x in range(0, W, 60):
                bg[:, x] = np.clip(bg[:, x] + [4, 10, 2], 0, 255)
            for y in range(0, H, 60):
                bg[y, :] = np.clip(bg[y, :] + [4, 10, 2], 0, 255)
            img = Image.fromarray(bg, "RGB")

        draw = ImageDraw.Draw(img)

        # 상단 녹색 악센트 바
        for y in range(8):
            intensity = int(255 * (1 - y / 8))
            draw.line([(0, y), (W, y)], fill=(
                int(C["green"][0] * intensity // 255),
                int(C["green"][1] * intensity // 255),
                0,
            ))

        self._draw_header(draw, slide_num, total_slides, data)
        self._draw_progress(draw, slide_num, total_slides)
        y_content = self._draw_content(draw, data)
        self._draw_script_box(draw, data)
        self._draw_bottom(draw, data)

        img.save(output_path, "PNG")
        return output_path

    # ── 헤더 (로고 / 슬라이드 번호 / 타임코드) ─────────────
    def _draw_header(self, draw, slide_num, total_slides, data):
        W = self.W
        # 왼쪽: NVIDIA
        draw.text((40, 32), "NVIDIA", font=self.fonts["small"], fill=C["green"])

        # 가운데: 슬라이드 번호
        num_text = f"{slide_num:02d} / {total_slides:02d}"
        bbox = draw.textbbox((0, 0), num_text, font=self.fonts["tiny"])
        tw = bbox[2] - bbox[0]
        cx = (W - tw) // 2
        pad = 18
        draw.rounded_rectangle([cx - pad, 26, cx + tw + pad, 72], radius=22,
                                fill=C["card_bg"], outline=C["green_dim"], width=1)
        draw.text((cx, 36), num_text, font=self.fonts["tiny"], fill=C["green"])

        # 오른쪽: 타임코드
        time_text = data.get("time", "")
        if time_text:
            bbox = draw.textbbox((0, 0), time_text, font=self.fonts["micro"])
            tw = bbox[2] - bbox[0]
            draw.text((W - 40 - tw, 40), time_text, font=self.fonts["micro"], fill=C["silver"])

    # ── 프로그레스 바 ───────────────────────────────────────
    def _draw_progress(self, draw, slide_num, total_slides):
        W = self.W
        bar_y = 86
        draw.rectangle([0, bar_y, W, bar_y + 5], fill=C["green_glow"])
        fill_w = int(W * slide_num / total_slides)
        draw.rectangle([0, bar_y, fill_w, bar_y + 5], fill=C["green"])

    # ── 메인 콘텐츠 ─────────────────────────────────────────
    def _draw_content(self, draw, data):
        W = self.W
        y = 118

        # Section tag
        section = data.get("section", "")
        if section:
            tag = f"  {section}  "
            bbox = draw.textbbox((0, 0), tag, font=self.fonts["tiny"])
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            cx = (W - tw) // 2
            draw.rounded_rectangle([cx - 6, y, cx + tw + 6, y + th + 18],
                                    radius=22, fill=C["green"])
            draw.text((cx, y + 7), tag, font=self.fonts["tiny"], fill=(0, 0, 0))
            y += th + 34

        # 아이콘 이모지
        icon = data.get("icon", "")
        if icon:
            try:
                bbox = draw.textbbox((0, 0), icon, font=self.fonts["huge"])
                iw = bbox[2] - bbox[0]
                draw.text(((W - iw) // 2, y), icon, font=self.fonts["huge"], fill=C["white"])
                y += 110
            except Exception:
                y += 40

        # 헤드라인 (NVIDIA Green)
        headline = data.get("headline", "")
        if headline:
            y = self._draw_centered(draw, headline, y, self.fonts["title"], C["green"], max_w=960) + 16

        # 서브 헤드라인 (실버)
        sub = data.get("sub_headline", "")
        if sub:
            y = self._draw_centered(draw, sub, y, self.fonts["medium"], C["silver"], max_w=940) + 24

        # 스탯 박스
        stats = data.get("stats") or []
        if stats:
            y = self._draw_stats(draw, stats, y) + 24

        # 칩 뱃지
        chips = data.get("chips") or []
        if chips:
            y = self._draw_chips(draw, chips, y)

        return y

    # ── 스크립트 박스 (하단 고정) ────────────────────────────
    def _draw_script_box(self, draw, data):
        W, H = self.W, self.H
        script = data.get("script", "")
        if not script:
            return

        bx, by = 36, H - 470
        bw, bh = W - 72, 400

        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=18,
                                fill=C["script_bg"], outline=C["border"], width=1)
        # 왼쪽 녹색 바
        draw.rounded_rectangle([bx, by, bx + 5, by + bh], radius=3, fill=C["green"])

        # 라벨
        draw.text((bx + 24, by + 16), "● VO SCRIPT", font=self.fonts["micro"], fill=C["green"])

        # 스크립트 텍스트
        lines = self._wrap(draw, script, self.fonts["small"], bw - 52)
        ty = by + 54
        max_lines = 9
        for i, line in enumerate(lines[:max_lines]):
            if i == max_lines - 1 and len(lines) > max_lines:
                line = line.rstrip()[:max(0, len(line) - 3)] + "..."
            draw.text((bx + 24, ty), line, font=self.fonts["small"], fill=(215, 215, 200))
            ty += 38

    # ── 하단 바 ─────────────────────────────────────────────
    def _draw_bottom(self, draw, data):
        W, H = self.W, self.H
        y = H - 44
        chips = data.get("chips") or []
        tags = " ".join(f"#{c}" for c in chips[:3])
        if tags:
            draw.text((40, y), tags, font=self.fonts["micro"], fill=C["green_dim"])
        draw.text((W - 220, y), "@AI테크뉴스", font=self.fonts["micro"], fill=(55, 75, 35))

    # ── 헬퍼: 중앙 정렬 텍스트 그리기 ──────────────────────
    def _draw_centered(self, draw, text, y, font, color, max_w):
        W = self.W
        lines = self._wrap(draw, text, font, max_w)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            draw.text(((W - tw) // 2, y), line, font=font, fill=color)
            y += th + 8
        return y

    # ── 헬퍼: 픽셀 너비 기반 word wrap ─────────────────────
    def _wrap(self, draw, text, font, max_w):
        result = []
        for para in text.replace("\r\n", "\n").split("\n"):
            words = para.split()
            if not words:
                result.append("")
                continue
            cur = []
            for word in words:
                test = " ".join(cur + [word])
                w = draw.textbbox((0, 0), test, font=font)[2]
                if w > max_w and cur:
                    result.append(" ".join(cur))
                    cur = [word]
                else:
                    cur.append(word)
            if cur:
                result.append(" ".join(cur))
        return result

    # ── 스탯 박스 ───────────────────────────────────────────
    def _draw_stats(self, draw, stats, y):
        W = self.W
        count = min(len(stats), 3)
        box_w = 270
        gap = 24
        total_w = count * box_w + (count - 1) * gap
        x0 = (W - total_w) // 2
        bh = 130

        for i, stat in enumerate(stats[:count]):
            x = x0 + i * (box_w + gap)
            draw.rounded_rectangle([x, y, x + box_w, y + bh], radius=16,
                                    fill=C["card_bg"], outline=C["green_dim"], width=1)
            val = str(stat.get("value", ""))
            bbox = draw.textbbox((0, 0), val, font=self.fonts["large"])
            vw = bbox[2] - bbox[0]
            draw.text((x + (box_w - vw) // 2, y + 10), val, font=self.fonts["large"], fill=C["green"])

            label = str(stat.get("label", ""))
            bbox = draw.textbbox((0, 0), label, font=self.fonts["micro"])
            lw = bbox[2] - bbox[0]
            draw.text((x + (box_w - lw) // 2, y + 92), label, font=self.fonts["micro"], fill=C["silver"])

        return y + bh

    # ── 칩 뱃지 ─────────────────────────────────────────────
    def _draw_chips(self, draw, chips, y):
        W = self.W
        gap = 14
        px, py = 28, 10
        ch = 52
        rows = []
        cur_row, cur_w = [], 0

        for chip in chips[:6]:
            bbox = draw.textbbox((0, 0), chip, font=self.fonts["small"])
            cw = bbox[2] - bbox[0] + px * 2
            if cur_w + cw + gap > W - 80 and cur_row:
                rows.append(cur_row)
                cur_row, cur_w = [(chip, cw)], cw + gap
            else:
                cur_row.append((chip, cw))
                cur_w += cw + gap
        if cur_row:
            rows.append(cur_row)

        for row in rows:
            total_w = sum(cw for _, cw in row) + gap * (len(row) - 1)
            x = (W - total_w) // 2
            for chip, cw in row:
                draw.rounded_rectangle([x, y, x + cw, y + ch], radius=26,
                                        fill=C["card_bg"], outline=C["green_dim"], width=1)
                bbox = draw.textbbox((0, 0), chip, font=self.fonts["small"])
                tw = bbox[2] - bbox[0]
                draw.text((x + (cw - tw) // 2, y + 10), chip, font=self.fonts["small"], fill=C["green"])
                x += cw + gap
            y += ch + 14

        return y

    # ══════════════════════════════════════════════════════════
    #  배경 이미지 지원
    # ══════════════════════════════════════════════════════════

    def _make_image_bg(self, image_path):
        """
        다운로드된 이미지를 슬라이드 배경으로 변환.
        1080×1920 center-crop → 어두운 오버레이 적용
        """
        W, H = self.W, self.H
        try:
            bg = Image.open(image_path).convert("RGB")
            bg = self._fit_image(bg, W, H)

            # 55% 어두운 오버레이 (텍스트 가독성 확보)
            overlay = Image.new("RGB", (W, H), (0, 0, 0))
            bg = Image.blend(bg, overlay, alpha=0.58)

            # 상단 녹색 그라디언트 tint
            tint = Image.new("RGB", (W, H), (10, 30, 0))
            for row in range(300):
                alpha = int(80 * (1 - row / 300))
                for col in range(W):
                    r, g, b = bg.getpixel((col, row))
                    tr, tg, tb = tint.getpixel((col, row))
                    bg.putpixel((col, row), (
                        min(255, r + tr * alpha // 255),
                        min(255, g + tg * alpha // 255),
                        min(255, b + tb * alpha // 255),
                    ))
            return bg
        except Exception as e:
            print(f"   [warn] 배경 이미지 로드 실패 ({e}) — 기본 배경 사용")
            bg = np.full((H, W, 3), C["bg"], dtype=np.uint8)
            return Image.fromarray(bg, "RGB")

    def _fit_image(self, img, target_w, target_h):
        """이미지를 target 크기에 맞게 center-crop"""
        scale = max(target_w / img.width, target_h / img.height)
        new_w = int(img.width * scale)
        new_h = int(img.height * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        return img.crop((left, top, left + target_w, top + target_h))

    # ══════════════════════════════════════════════════════════
    #  자막 렌더링 (video_builder에서 호출)
    # ══════════════════════════════════════════════════════════

    def split_subtitle_chunks(self, text, duration, max_words=12):
        """
        스크립트 텍스트를 자막 청크로 분할.
        반환: [(chunk_text, chunk_duration), ...]
        """
        import re
        if not text or not text.strip():
            return []

        # 문장 단위 분리 (한국어 + 영어 공통)
        sentences = re.split(r"(?<=[.!?。！？])\s+", text.strip())
        chunks = []
        for sent in sentences:
            words = sent.split()
            if len(words) <= max_words:
                if sent.strip():
                    chunks.append(sent.strip())
            else:
                for i in range(0, len(words), max_words):
                    part = " ".join(words[i : i + max_words])
                    if part.strip():
                        chunks.append(part.strip())

        if not chunks:
            return []

        # 글자수 비율로 지속 시간 배분 (최소 1.5초 보장)
        total_chars = sum(len(c) for c in chunks)
        result = []
        for chunk in chunks:
            ratio = len(chunk) / total_chars if total_chars > 0 else 1 / len(chunks)
            dur = max(1.5, duration * ratio)
            result.append((chunk, dur))

        # 총 지속시간을 실제 오디오 길이에 맞춤 (비율 조정)
        total_assigned = sum(d for _, d in result)
        factor = duration / total_assigned if total_assigned > 0 else 1.0
        result = [(t, d * factor) for t, d in result]

        return result

    def render_subtitle_frame(self, base_array, text):
        """
        슬라이드 numpy 배열 위에 자막 바를 합성한 새 numpy 배열 반환.
        (원본 배열은 변경하지 않음)
        """
        W, H = self.W, self.H
        img = Image.fromarray(base_array.copy()).convert("RGBA")

        # 반투명 검정 자막 바 (하단)
        bar_h = 190
        bar_y = H - bar_h - 50
        bar = Image.new("RGBA", (W, bar_h), (0, 0, 0, 195))
        img.paste(bar, (0, bar_y), bar)

        img_rgb = img.convert("RGB")
        draw = ImageDraw.Draw(img_rgb)

        # 텍스트 래핑
        lines = self._wrap(draw, text, self.fonts["normal"], W - 80)
        line_h = 46
        total_h = len(lines) * line_h
        ty = bar_y + (bar_h - total_h) // 2

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=self.fonts["normal"])
            tw = bbox[2] - bbox[0]
            x = (W - tw) // 2
            # 그림자 (가독성)
            draw.text((x + 2, ty + 2), line, font=self.fonts["normal"], fill=(0, 0, 0))
            # 흰색 텍스트
            draw.text((x, ty), line, font=self.fonts["normal"], fill=(255, 255, 255))
            ty += line_h

        return np.array(img_rgb)
