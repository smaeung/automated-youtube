"""
YouTube Shorts script generation module using the Claude API.
Supports 12 output languages via LANG_CONFIG.
"""

import os
import json
import anthropic

# ── Language configuration ────────────────────────────────────
LANG_CONFIG = {
    "ko": {
        "name": "Korean",
        "native": "한국어",
        "channel": "@AI테크뉴스",
        "duration_map": {"1min": "1분", "3min": "3분", "5min": "5분", "10min": "10분"},
    },
    "en": {
        "name": "English",
        "native": "English",
        "channel": "@AITechNews",
        "duration_map": {"1min": "1 min", "3min": "3 min", "5min": "5 min", "10min": "10 min"},
    },
    "ja": {
        "name": "Japanese",
        "native": "日本語",
        "channel": "@AIテックニュース",
        "duration_map": {"1min": "1分", "3min": "3分", "5min": "5分", "10min": "10分"},
    },
    "zh": {
        "name": "Chinese (Simplified)",
        "native": "中文",
        "channel": "@AI科技新闻",
        "duration_map": {"1min": "1分钟", "3min": "3分钟", "5min": "5分钟", "10min": "10分钟"},
    },
    "es": {
        "name": "Spanish",
        "native": "Español",
        "channel": "@AITechNoticias",
        "duration_map": {"1min": "1 min", "3min": "3 min", "5min": "5 min", "10min": "10 min"},
    },
    "fr": {
        "name": "French",
        "native": "Français",
        "channel": "@AITechActu",
        "duration_map": {"1min": "1 min", "3min": "3 min", "5min": "5 min", "10min": "10 min"},
    },
    "de": {
        "name": "German",
        "native": "Deutsch",
        "channel": "@AITechNews",
        "duration_map": {"1min": "1 Min", "3min": "3 Min", "5min": "5 Min", "10min": "10 Min"},
    },
    "pt": {
        "name": "Portuguese (Brazilian)",
        "native": "Português",
        "channel": "@AITechNoticias",
        "duration_map": {"1min": "1 min", "3min": "3 min", "5min": "5 min", "10min": "10 min"},
    },
    "ar": {
        "name": "Arabic",
        "native": "العربية",
        "channel": "@AITechNews",
        "duration_map": {"1min": "1 دقيقة", "3min": "3 دقائق", "5min": "5 دقائق", "10min": "10 دقائق"},
    },
    "hi": {
        "name": "Hindi",
        "native": "हिन्दी",
        "channel": "@AITechHindi",
        "duration_map": {"1min": "1 मिनट", "3min": "3 मिनट", "5min": "5 मिनट", "10min": "10 मिनट"},
    },
    "it": {
        "name": "Italian",
        "native": "Italiano",
        "channel": "@AITechNotizie",
        "duration_map": {"1min": "1 min", "3min": "3 min", "5min": "5 min", "10min": "10 min"},
    },
    "ru": {
        "name": "Russian",
        "native": "Русский",
        "channel": "@AIТехНовости",
        "duration_map": {"1min": "1 мин", "3min": "3 мин", "5min": "5 мин", "10min": "10 мин"},
    },
}


class ScriptGenerator:
    MODEL = "claude-sonnet-4-6"

    def __init__(self, lang="ko"):
        self.lang = lang
        self.lang_cfg = LANG_CONFIG.get(lang, LANG_CONFIG["en"])
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not set.\n"
                "Create a .env file and add your API key."
            )
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate(self, topic, topic_info=None, num_slides=8, duration="5min"):
        """Generate a JSON script for the given topic in the configured language."""
        if topic_info is None:
            topic_info = {}

        cfg = self.lang_cfg
        lang_name = cfg["name"]
        duration_label = cfg["duration_map"].get(duration, duration)
        description = topic_info.get("description", "")
        reason = topic_info.get("reason", "")

        prompt = f"""You are a professional YouTube Shorts scriptwriter for a tech channel.
Generate ALL content ENTIRELY in {lang_name} language (not English, not any other language).

Topic: {topic}
Background: {description}
Reason selected: {reason}
Video length: {duration_label}
Number of slides: {num_slides}

Return ONLY a pure JSON object — no code blocks, no explanations, no markdown:

{{
  "youtube_title": "Clickable title in {lang_name} (under 60 chars, include numbers or impact)",
  "topic": "{topic}",
  "duration": "{duration}",
  "hashtags": ["#tag1InLang", "#tag2InLang", "#tag3InLang", "#tag4InLang", "#tag5InLang"],
  "description": "YouTube video description in {lang_name} (under 200 chars, key summary)",
  "slides": [
    {{
      "id": 1,
      "section": "HOOK",
      "time": "0:00-0:30",
      "icon": "💡",
      "headline": "Strong headline in {lang_name} (under 30 chars)",
      "sub_headline": "Sub-headline in {lang_name} (under 50 chars)",
      "chips": ["keyword1", "keyword2", "keyword3"],
      "stats": [{{"value": "number", "label": "description in {lang_name}"}}],
      "script": "Narration in {lang_name} for this slide. Natural, impactful, engaging. 30-40 seconds of speech."
    }}
  ]
}}

Slide structure ({num_slides} slides):
- Slide 1: HOOK — shocking fact or number, spark curiosity immediately
- Slide 2: INTRO — topic background and why it matters
- Slides 3–{num_slides - 2}: CORE — one key point per slide, data-driven
- Slide {num_slides - 1}: IMPACT — what this means for the viewer
- Slide {num_slides}: CTA — subscribe/like call-to-action, tease next video

CRITICAL RULES:
- ALL text (title, scripts, hashtags, labels, descriptions, chips) MUST be in {lang_name}
- Each "script" field is the spoken narration for that slide (30-40 seconds worth)
- "stats": include only when there are real numbers (otherwise use [])
- "icon": exactly one relevant emoji per slide
- "chips": 3-4 short keywords in {lang_name}
- Tone: professional yet accessible, impactful, fact-focused"""

        message = self.client.messages.create(
            model=self.MODEL,
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = message.content[0].text.strip()

        # Check if the response was truncated
        if message.stop_reason == "max_tokens":
            print("   [warn] Response truncated — attempting JSON repair...")
            raw = self._repair_json(raw)

        # Strip code block wrappers if present
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        try:
            script = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"   [warn] JSON parse failed ({e}), retrying with repair...")
            raw = self._repair_json(raw)
            script = json.loads(raw)

        return script

    def _repair_json(self, raw):
        """Attempt to recover a truncated JSON response by closing open slides array."""
        brace_depth = 0
        last_safe = -1
        in_string = False
        escape = False

        for i, ch in enumerate(raw):
            if escape:
                escape = False
                continue
            if ch == "\\" and in_string:
                escape = True
                continue
            if ch == '"' and not escape:
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "{":
                brace_depth += 1
            elif ch == "}":
                brace_depth -= 1
                if brace_depth == 1:   # a slide object just closed inside the slides array
                    last_safe = i

        if last_safe == -1:
            raise ValueError("JSON repair failed — response is too short to recover")

        truncated = raw[: last_safe + 1]
        truncated = truncated.rstrip().rstrip(",")
        repaired = truncated + "\n  ]\n}"
        return repaired
