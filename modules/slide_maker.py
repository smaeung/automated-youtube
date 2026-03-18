"""
Slide image generation module using PIL/Pillow.
Resolution: 1080x1920 (9:16 YouTube Shorts)
Language support: ko, en, ja, zh, es, fr, de, pt, ar, hi, it, ru
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── Color palette ─────────────────────────────────────────────
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

# ── Font candidates by language (priority order) ──────────────
_WIN = r"C:\Windows\Fonts"
_LINUX_NOTO = "/usr/share/fonts/truetype/noto"
_LINUX_NOTO_OT = "/usr/share/fonts/opentype/noto"

FONT_CANDIDATES_BY_LANG = {
    # Korean
    "ko": [
        f"{_WIN}\\malgunbd.ttf",
        f"{_WIN}\\malgun.ttf",
        f"{_WIN}\\gulim.ttc",
        f"{_LINUX_NOTO}/NotoSansCJK-Bold.ttc",
        f"{_LINUX_NOTO_OT}/NotoSansCJK-Bold.ttc",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    ],
    # Japanese
    "ja": [
        f"{_WIN}\\YuGothB.ttc",
        f"{_WIN}\\meiryo.ttc",
        f"{_WIN}\\msgothic.ttc",
        f"{_WIN}\\malgunbd.ttf",
        f"{_LINUX_NOTO}/NotoSansCJK-Bold.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    ],
    # Chinese Simplified
    "zh": [
        f"{_WIN}\\msyh.ttc",
        f"{_WIN}\\simhei.ttf",
        f"{_WIN}\\simsun.ttc",
        f"{_WIN}\\malgunbd.ttf",
        f"{_LINUX_NOTO}/NotoSansCJK-Bold.ttc",
        "/System/Library/Fonts/PingFang.ttc",
    ],
    # Arabic — note: PIL renders RTL as LTR visually
    "ar": [
        f"{_WIN}\\arabtype.ttf",
        f"{_WIN}\\trado.ttf",
        f"{_WIN}\\arial.ttf",
        f"{_LINUX_NOTO}/NotoNaskhArabic-Bold.ttf",
        "/System/Library/Fonts/GeezaPro.ttc",
    ],
    # Hindi / Devanagari
    "hi": [
        f"{_WIN}\\NirmalaB.ttf",
        f"{_WIN}\\Nirmala.ttf",
        f"{_WIN}\\arial.ttf",
        f"{_LINUX_NOTO}/NotoSansDevanagari-Bold.ttf",
    ],
    # Russian / Cyrillic
    "ru": [
        f"{_WIN}\\arialbd.ttf",
        f"{_WIN}\\arial.ttf",
        f"{_WIN}\\malgunbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
}

# Latin-script languages share the same font list
_LATIN_FONTS = [
    f"{_WIN}\\arialbd.ttf",
    f"{_WIN}\\arial.ttf",
    f"{_WIN}\\malgunbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]
for _lang in ("en", "es", "fr", "de", "pt", "it"):
    FONT_CANDIDATES_BY_LANG[_lang] = _LATIN_FONTS

# ── Channel name by language ──────────────────────────────────
CHANNEL_BY_LANG = {
    "ko": "@AI테크뉴스",
    "en": "@AITechNews",
    "ja": "@AIテックニュース",
    "zh": "@AI科技新闻",
    "es": "@AITechNoticias",
    "fr": "@AITechActu",
    "de": "@AITechNews",
    "pt": "@AITechNoticias",
    "ar": "@AITechNews",
    "hi": "@AITechHindi",
    "it": "@AITechNotizie",
    "ru": "@AIТехНовости",
}


def _find_font(lang="ko"):
    candidates = FONT_CANDIDATES_BY_LANG.get(lang, _LATIN_FONTS)
    for p in candidates:
        if os.path.exists(p):
            return p
    # Last resort: find any available CJK font
    for p in FONT_CANDIDATES_BY_LANG["ko"]:
        if os.path.exists(p):
            return p
    return None


class SlideMaker:
    W = 1080
    H = 1920

    def __init__(self, output_dir, searcher=None, images_dir=None, lang="ko"):
        self.output_dir = Path(output_dir)
        self.searcher = searcher        # ImageSearcher instance (skipped if None)
        self.images_dir = Path(images_dir) if images_dir else None
        self.lang = lang
        self.channel_name = CHANNEL_BY_LANG.get(lang, "@AITechNews")
        self.font_path = _find_font(lang)
        self.fonts = self._load_fonts()

    # ── Load fonts ───────────────────────────────────────────
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

    # ── Generate all slides ──────────────────────────────────
    def create_all(self, script):
        slides = script.get("slides", [])
        topic = script.get("topic", "")
        paths = []
        total = len(slides)

        for i, slide_data in enumerate(slides):
            # Search for background image (when searcher is available)
            bg_image_path = None
            if self.searcher and self.images_dir:
                self.images_dir.mkdir(parents=True, exist_ok=True)
                query = f"{slide_data.get('headline', '')} {topic}"
                img_out = str(self.images_dir / f"bg_{i+1:02d}.jpg")
                bg_image_path = self.searcher.search(query, img_out)
                status = "image downloaded" if bg_image_path else "default bg"
                print(f"   [img] [{i+1}/{total}] {slide_data.get('section', '')} — {status}")
            else:
                print(f"   [img] [{i+1}/{total}] {slide_data.get('section', '')} done")

            path = self.output_dir / f"slide_{i+1:02d}.png"
            self.create_slide(slide_data, i + 1, total, str(path), bg_image_path=bg_image_path)
            paths.append(str(path))

        return paths

    # ── Generate a single slide ──────────────────────────────
    def create_slide(self, data, slide_num, total_slides, output_path, bg_image_path=None):
        W, H = self.W, self.H

        # Background: use image if available, otherwise draw gradient
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

        # Top green accent bar (fading gradient)
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

    # ── Header (logo / slide number / timecode) ──────────────
    def _draw_header(self, draw, slide_num, total_slides, data):
        W = self.W
        # Left: NVIDIA logo text
        draw.text((40, 32), "NVIDIA", font=self.fonts["small"], fill=C["green"])

        # Center: slide number badge
        num_text = f"{slide_num:02d} / {total_slides:02d}"
        bbox = draw.textbbox((0, 0), num_text, font=self.fonts["tiny"])
        tw = bbox[2] - bbox[0]
        cx = (W - tw) // 2
        pad = 18
        draw.rounded_rectangle([cx - pad, 26, cx + tw + pad, 72], radius=22,
                                fill=C["card_bg"], outline=C["green_dim"], width=1)
        draw.text((cx, 36), num_text, font=self.fonts["tiny"], fill=C["green"])

        # Right: timecode
        time_text = data.get("time", "")
        if time_text:
            bbox = draw.textbbox((0, 0), time_text, font=self.fonts["micro"])
            tw = bbox[2] - bbox[0]
            draw.text((W - 40 - tw, 40), time_text, font=self.fonts["micro"], fill=C["silver"])

    # ── Progress bar ─────────────────────────────────────────
    def _draw_progress(self, draw, slide_num, total_slides):
        W = self.W
        bar_y = 86
        draw.rectangle([0, bar_y, W, bar_y + 5], fill=C["green_glow"])
        fill_w = int(W * slide_num / total_slides)
        draw.rectangle([0, bar_y, fill_w, bar_y + 5], fill=C["green"])

    # ── Main content area ────────────────────────────────────
    def _draw_content(self, draw, data):
        W = self.W
        y = 118

        # Section tag badge
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

        # Icon emoji
        icon = data.get("icon", "")
        if icon:
            try:
                bbox = draw.textbbox((0, 0), icon, font=self.fonts["huge"])
                iw = bbox[2] - bbox[0]
                draw.text(((W - iw) // 2, y), icon, font=self.fonts["huge"], fill=C["white"])
                y += 110
            except Exception:
                y += 40

        # Headline (NVIDIA Green)
        headline = data.get("headline", "")
        if headline:
            y = self._draw_centered(draw, headline, y, self.fonts["title"], C["green"], max_w=960) + 16

        # Sub-headline (silver)
        sub = data.get("sub_headline", "")
        if sub:
            y = self._draw_centered(draw, sub, y, self.fonts["medium"], C["silver"], max_w=940) + 24

        # Stats boxes
        stats = data.get("stats") or []
        if stats:
            y = self._draw_stats(draw, stats, y) + 24

        # Chip badges
        chips = data.get("chips") or []
        if chips:
            y = self._draw_chips(draw, chips, y)

        return y

    # ── VO script box (pinned to bottom) ─────────────────────
    def _draw_script_box(self, draw, data):
        W, H = self.W, self.H
        script = data.get("script", "")
        if not script:
            return

        bx, by = 36, H - 470
        bw, bh = W - 72, 400

        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=18,
                                fill=C["script_bg"], outline=C["border"], width=1)
        # Left green accent bar
        draw.rounded_rectangle([bx, by, bx + 5, by + bh], radius=3, fill=C["green"])

        # Label
        draw.text((bx + 24, by + 16), "● VO SCRIPT", font=self.fonts["micro"], fill=C["green"])

        # Script text (truncated if too long)
        lines = self._wrap(draw, script, self.fonts["small"], bw - 52)
        ty = by + 54
        max_lines = 9
        for i, line in enumerate(lines[:max_lines]):
            if i == max_lines - 1 and len(lines) > max_lines:
                line = line.rstrip()[:max(0, len(line) - 3)] + "..."
            draw.text((bx + 24, ty), line, font=self.fonts["small"], fill=(215, 215, 200))
            ty += 38

    # ── Bottom bar ───────────────────────────────────────────
    def _draw_bottom(self, draw, data):
        W, H = self.W, self.H
        y = H - 44
        chips = data.get("chips") or []
        tags = " ".join(f"#{c}" for c in chips[:3])
        if tags:
            draw.text((40, y), tags, font=self.fonts["micro"], fill=C["green_dim"])
        draw.text((W - 220, y), self.channel_name, font=self.fonts["micro"], fill=(55, 75, 35))

    # ── Helper: draw centered text ───────────────────────────
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

    # ── Helper: pixel-width-based word wrap ──────────────────
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

    # ── Stats boxes ──────────────────────────────────────────
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

    # ── Chip badges ──────────────────────────────────────────
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
    #  Background image support
    # ══════════════════════════════════════════════════════════

    def _make_image_bg(self, image_path):
        """Convert a downloaded photo into a slide background.
        Center-crops to 1080×1920 and applies a dark overlay for legibility."""
        W, H = self.W, self.H
        try:
            bg = Image.open(image_path).convert("RGB")
            bg = self._fit_image(bg, W, H)

            # Dark overlay for text legibility (~58% opacity)
            overlay = Image.new("RGB", (W, H), (0, 0, 0))
            bg = Image.blend(bg, overlay, alpha=0.58)

            # Green gradient tint at the top
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
            print(f"   [warn] Failed to load background image ({e}) — using default")
            bg = np.full((H, W, 3), C["bg"], dtype=np.uint8)
            return Image.fromarray(bg, "RGB")

    def _fit_image(self, img, target_w, target_h):
        """Scale and center-crop image to exact target dimensions."""
        scale = max(target_w / img.width, target_h / img.height)
        new_w = int(img.width * scale)
        new_h = int(img.height * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        return img.crop((left, top, left + target_w, top + target_h))

    # ══════════════════════════════════════════════════════════
    #  Subtitle rendering (called by video_builder)
    # ══════════════════════════════════════════════════════════

    def split_subtitle_chunks(self, text, duration, max_words=12):
        """Split script text into timed subtitle chunks.
        Returns: [(chunk_text, chunk_duration), ...]"""
        import re
        if not text or not text.strip():
            return []

        # Split by sentence boundary (works for Korean and Latin scripts)
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

        # Distribute duration by character count (min 1.5 s per chunk)
        total_chars = sum(len(c) for c in chunks)
        result = []
        for chunk in chunks:
            ratio = len(chunk) / total_chars if total_chars > 0 else 1 / len(chunks)
            dur = max(1.5, duration * ratio)
            result.append((chunk, dur))

        # Scale all durations to match the actual audio length
        total_assigned = sum(d for _, d in result)
        factor = duration / total_assigned if total_assigned > 0 else 1.0
        result = [(t, d * factor) for t, d in result]

        return result

    def render_subtitle_frame(self, base_array, text):
        """Composite a subtitle bar onto a slide numpy array.
        Returns a new array — the original is not modified."""
        W, H = self.W, self.H
        img = Image.fromarray(base_array.copy()).convert("RGBA")

        # Semi-transparent black subtitle bar at the bottom
        bar_h = 190
        bar_y = H - bar_h - 50
        bar = Image.new("RGBA", (W, bar_h), (0, 0, 0, 195))
        img.paste(bar, (0, bar_y), bar)

        img_rgb = img.convert("RGB")
        draw = ImageDraw.Draw(img_rgb)

        # Word-wrap text to fit inside the bar
        lines = self._wrap(draw, text, self.fonts["normal"], W - 80)
        line_h = 46
        total_h = len(lines) * line_h
        ty = bar_y + (bar_h - total_h) // 2

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=self.fonts["normal"])
            tw = bbox[2] - bbox[0]
            x = (W - tw) // 2
            # Drop shadow for readability
            draw.text((x + 2, ty + 2), line, font=self.fonts["normal"], fill=(0, 0, 0))
            # White text
            draw.text((x, ty), line, font=self.fonts["normal"], fill=(255, 255, 255))
            ty += line_h

        return np.array(img_rgb)
