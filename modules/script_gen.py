"""
Claude API를 이용한 YouTube Shorts 스크립트 생성 모듈
"""

import os
import json
import anthropic


class ScriptGenerator:
    MODEL = "claude-sonnet-4-6"

    def __init__(self, lang="ko"):
        self.lang = lang
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY 환경변수가 없습니다.\n"
                ".env 파일을 만들고 API 키를 입력하세요."
            )
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate(self, topic, topic_info=None, num_slides=8, duration="5min"):
        """주제 → JSON 스크립트 생성"""
        if topic_info is None:
            topic_info = {}

        duration_label = {
            "1min": "1분", "3min": "3분", "5min": "5분", "10min": "10분"
        }.get(duration, duration)

        description = topic_info.get("description", "")
        reason = topic_info.get("reason", "")

        prompt = f"""당신은 한국 유튜브 테크 채널 전문 작가입니다.

주제: {topic}
배경: {description}
선정 이유: {reason}
영상 길이: {duration_label}
슬라이드 수: {num_slides}개

아래 JSON 형식으로 YouTube Shorts 스크립트를 작성하세요.
타겟: IT·테크 관심자, 개발자, 일반 대중
톤: 전문적이지만 이해하기 쉽게, 임팩트 있게, 숫자와 사실 중심

반드시 순수 JSON만 반환하세요 (코드블록 없이, 설명 없이):

{{
  "youtube_title": "클릭하고 싶은 제목 (60자 이내, 숫자·충격 포함)",
  "topic": "{topic}",
  "duration": "{duration}",
  "hashtags": ["#태그1", "#태그2", "#태그3", "#태그4", "#태그5"],
  "description": "YouTube 영상 설명 (200자 이내, 핵심 요약)",
  "slides": [
    {{
      "id": 1,
      "section": "HOOK",
      "time": "0:00-0:30",
      "icon": "💡",
      "headline": "강렬한 헤드라인 (15자 이내)",
      "sub_headline": "서브 헤드라인 (25자 이내)",
      "chips": ["키워드1", "키워드2", "키워드3"],
      "stats": [{{"value": "숫자", "label": "설명"}}],
      "script": "이 슬라이드 나레이션. 자연스럽고 임팩트 있게. 30~40초 분량. 시청자가 계속 보고 싶도록."
    }}
  ]
}}

슬라이드 {num_slides}개 구성:
- 1번: HOOK — 충격적 사실/숫자로 시작, 호기심 자극
- 2번: 소개 — 주제 배경과 왜 중요한지
- 3~{num_slides-2}번: 핵심 내용 — 슬라이드당 하나의 핵심 포인트
- {num_slides-1}번: 임팩트 — 왜 이게 중요한가, 시청자에게 주는 의미
- {num_slides}번: CTA — 구독·좋아요 유도, 다음 영상 예고

중요:
- 각 script는 해당 슬라이드에서 말할 나레이션 (30~40초 분량)
- stats는 해당 슬라이드에 수치가 있을 때만 포함 (없으면 [])
- icon은 내용을 대표하는 이모지 1개
- chips는 3~4개 키워드"""

        message = self.client.messages.create(
            model=self.MODEL,
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = message.content[0].text.strip()

        # 응답이 잘렸는지 확인
        if message.stop_reason == "max_tokens":
            print("   [warn] Response truncated — attempting JSON repair...")
            raw = self._repair_json(raw)

        # 코드블록 제거
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
        """잘린 JSON을 최대한 복구 — slides 배열을 닫아줌"""
        # 마지막 완전한 슬라이드 객체까지만 잘라냄
        # "script" 필드가 닫힌 마지막 위치를 찾음
        import re

        # 마지막으로 완전히 닫힌 슬라이드 } 위치 찾기
        # 슬라이드 객체는 }로 끝남 — 역방향 탐색
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
                if brace_depth == 1:   # slides 배열 안의 슬라이드 닫힘
                    last_safe = i

        if last_safe == -1:
            raise ValueError("JSON 복구 불가 — 응답이 너무 짧습니다")

        # last_safe 이후를 잘라내고 배열·객체 닫기
        truncated = raw[: last_safe + 1]
        truncated = truncated.rstrip().rstrip(",")
        repaired = truncated + "\n  ]\n}"
        return repaired
