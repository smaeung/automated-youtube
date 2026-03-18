"""
트렌드 탐색 모듈
1차: pytrends (Google Trends Korea)
2차 fallback: 날짜 기반 기본 트렌드 목록
"""

from datetime import datetime

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False


class TrendFinder:
    def __init__(self, lang="ko"):
        self.lang = lang
        self.geo = "KR" if lang == "ko" else "US"

    def get_trends(self, limit=5):
        """여러 소스에서 트렌드 수집, 최적 주제 리스트 반환"""
        # 1차: Google Trends
        if PYTRENDS_AVAILABLE:
            try:
                trends = self._google_trends(limit)
                if trends:
                    return trends
            except Exception as e:
                print(f"   ⚠️  Google Trends 오류: {e}")

        # 2차: fallback
        return self._default_trends(limit)

    def _google_trends(self, limit):
        pytrends = TrendReq(hl=self.lang, tz=540)
        region = "south_korea" if self.geo == "KR" else "united_states"
        df = pytrends.trending_searches(pn=region)
        results = []
        for _, row in df.head(limit).iterrows():
            keyword = str(row[0])
            results.append({
                "topic": keyword,
                "reason": "Google Trends 실시간 급상승",
                "description": f"Google 검색에서 '{keyword}'가 급상승 중입니다.",
                "source": "google_trends",
            })
        return results

    def _default_trends(self, limit):
        """현재 시점 기반 기본 트렌드 목록"""
        now = datetime.now()
        month = now.month

        topics = [
            {
                "topic": "NVIDIA GTC 2026 AI 혁명",
                "reason": "GTC 2026 개최 (3월 16~19일)",
                "description": "젠슨 황이 발표한 Vera Rubin, Groq 3 LPU, DLSS 5 등 최신 AI 기술",
            },
            {
                "topic": "에이전틱 AI 시대 완벽 정리",
                "reason": "2026년 최대 AI 키워드",
                "description": "스스로 계획하고 행동하는 AI 에이전트 기술의 현재와 미래",
            },
            {
                "topic": "2026 AI 반도체 전쟁",
                "reason": "NVIDIA vs AMD vs Intel 경쟁 심화",
                "description": "AI 칩 시장 패권 경쟁 — Blackwell, MI300X, Gaudi 3 비교",
            },
            {
                "topic": "ChatGPT vs Claude 4 비교",
                "reason": "AI 모델 대전 관심 급증",
                "description": "2026년 최강 AI 모델은? 성능·가격·사용성 완전 비교",
            },
            {
                "topic": "AI 직업 대체 현실",
                "reason": "AI 자동화 사회적 이슈",
                "description": "AI가 실제로 대체하고 있는 직업들과 살아남는 방법",
            },
            {
                "topic": "삼성 Galaxy AI 기능 총정리",
                "reason": "스마트폰 AI 대중화",
                "description": "Galaxy S25 시리즈의 AI 기능 완전 분석",
            },
        ]

        return topics[:limit]
