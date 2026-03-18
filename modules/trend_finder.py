"""
트렌드 탐색 모듈 (다국어 지원)
1차: pytrends (Google Trends — 언어별 국가)
2차 fallback: 날짜 기반 기본 트렌드 목록
"""

from datetime import datetime

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False

# ── 언어 → Google Trends 지역/언어 매핑 ───────────────────────
GEO_MAP = {
    "ko": ("KR", "ko",    "south_korea"),
    "en": ("US", "en",    "united_states"),
    "ja": ("JP", "ja",    "japan"),
    "zh": ("CN", "zh-CN", "china"),
    "es": ("ES", "es",    "spain"),
    "fr": ("FR", "fr",    "france"),
    "de": ("DE", "de",    "germany"),
    "pt": ("BR", "pt-BR", "brazil"),
    "ar": ("SA", "ar",    "saudi_arabia"),
    "hi": ("IN", "hi",    "india"),
    "it": ("IT", "it",    "italy"),
    "ru": ("RU", "ru",    "russia"),
}

# ── 언어별 기본 트렌드 목록 (pytrends 실패 시 fallback) ───────
DEFAULT_TOPICS = {
    "ko": [
        {"topic": "NVIDIA GTC 2026 AI 혁명", "reason": "GTC 2026 개최 (3월 16~19일)", "description": "젠슨 황이 발표한 Vera Rubin, Groq 3 LPU, DLSS 5 등 최신 AI 기술"},
        {"topic": "에이전틱 AI 시대 완벽 정리", "reason": "2026년 최대 AI 키워드", "description": "스스로 계획하고 행동하는 AI 에이전트 기술의 현재와 미래"},
        {"topic": "2026 AI 반도체 전쟁", "reason": "NVIDIA vs AMD vs Intel 경쟁 심화", "description": "AI 칩 시장 패권 경쟁"},
        {"topic": "ChatGPT vs Claude 4 비교", "reason": "AI 모델 대전 관심 급증", "description": "2026년 최강 AI 모델 완전 비교"},
        {"topic": "AI 직업 대체 현실", "reason": "AI 자동화 사회적 이슈", "description": "AI가 실제로 대체하고 있는 직업들"},
        {"topic": "삼성 Galaxy AI 기능 총정리", "reason": "스마트폰 AI 대중화", "description": "Galaxy S25 시리즈의 AI 기능 완전 분석"},
    ],
    "en": [
        {"topic": "NVIDIA GTC 2026: The AI Revolution", "reason": "GTC 2026 held March 16-19", "description": "Jensen Huang reveals Vera Rubin GPU, next-gen AI chips"},
        {"topic": "Agentic AI Explained", "reason": "#1 AI trend of 2026", "description": "AI agents that plan and act autonomously"},
        {"topic": "2026 AI Chip War", "reason": "NVIDIA vs AMD vs Intel intensifies", "description": "Who wins the AI semiconductor race?"},
        {"topic": "ChatGPT vs Claude 4 Showdown", "reason": "AI model competition heats up", "description": "The best AI model of 2026 compared"},
        {"topic": "Jobs AI Will Replace in 2026", "reason": "AI automation impact", "description": "Which careers are most at risk and how to adapt"},
        {"topic": "Apple Intelligence vs Google Gemini", "reason": "On-device AI battle", "description": "Who has the best AI assistant in 2026?"},
    ],
    "ja": [
        {"topic": "NVIDIA GTC 2026 AI革命", "reason": "GTC 2026開催（3月16〜19日）", "description": "ジェンスン・フアンが発表した次世代AI技術"},
        {"topic": "エージェント型AIの時代", "reason": "2026年最大のAIトレンド", "description": "自律的に計画・行動するAIエージェント"},
        {"topic": "2026 AIチップ戦争", "reason": "NVIDIA vs AMD vs Intel競争激化", "description": "AI半導体市場の覇権争い"},
        {"topic": "ChatGPT vs Claude 4比較", "reason": "AIモデル競争が激化", "description": "2026年最強のAIモデルを徹底比較"},
        {"topic": "AIが奪う仕事2026", "reason": "AI自動化の社会的影響", "description": "AIに代替される職業と生き残る方法"},
        {"topic": "Google Gemini Ultra完全解説", "reason": "AIアシスタント最新動向", "description": "Geminiの最新機能と活用法"},
    ],
    "zh": [
        {"topic": "NVIDIA GTC 2026 AI革命", "reason": "GTC 2026（3月16-19日）", "description": "黄仁勋发布Vera Rubin等最新AI技术"},
        {"topic": "AI智能体时代来临", "reason": "2026年最热AI趋势", "description": "能自主规划行动的AI代理技术"},
        {"topic": "2026年AI芯片大战", "reason": "NVIDIA vs AMD vs Intel竞争加剧", "description": "AI半导体市场争霸"},
        {"topic": "DeepSeek vs ChatGPT对比", "reason": "AI大模型竞争", "description": "2026年最强AI模型全面对比"},
        {"topic": "AI将取代哪些工作", "reason": "AI自动化社会影响", "description": "AI正在替代的职业和应对策略"},
        {"topic": "华为昇腾AI芯片解析", "reason": "国产AI芯片崛起", "description": "华为AI芯片现状与前景"},
    ],
    "es": [
        {"topic": "NVIDIA GTC 2026: La Revolución IA", "reason": "GTC 2026 (16-19 marzo)", "description": "Jensen Huang presenta la nueva generación de IA"},
        {"topic": "Era de la IA Agéntica", "reason": "Tendencia #1 de IA en 2026", "description": "Agentes de IA que planean y actúan de forma autónoma"},
        {"topic": "Guerra de Chips IA 2026", "reason": "NVIDIA vs AMD vs Intel", "description": "¿Quién gana la carrera de semiconductores de IA?"},
        {"topic": "ChatGPT vs Claude 4", "reason": "Competencia de modelos IA", "description": "El mejor modelo de IA de 2026 comparado"},
        {"topic": "Empleos que reemplazará la IA", "reason": "Impacto de la automatización", "description": "Qué carreras están en riesgo y cómo adaptarse"},
        {"topic": "Meta AI vs Google Gemini", "reason": "Batalla de asistentes IA", "description": "Comparativa de los mejores asistentes de IA"},
    ],
    "fr": [
        {"topic": "NVIDIA GTC 2026: La Révolution IA", "reason": "GTC 2026 (16-19 mars)", "description": "Jensen Huang présente la nouvelle génération d'IA"},
        {"topic": "L'ère de l'IA Agentique", "reason": "Tendance IA #1 en 2026", "description": "Des agents IA qui planifient et agissent de façon autonome"},
        {"topic": "Guerre des Puces IA 2026", "reason": "NVIDIA vs AMD vs Intel", "description": "Qui remportera la course aux semi-conducteurs IA?"},
        {"topic": "ChatGPT vs Claude 4", "reason": "Compétition des modèles IA", "description": "Le meilleur modèle d'IA de 2026 comparé"},
        {"topic": "Emplois menacés par l'IA", "reason": "Impact de l'automatisation", "description": "Quels métiers sont à risque et comment s'adapter"},
        {"topic": "Apple Intelligence vs Google Gemini", "reason": "Bataille des assistants IA", "description": "Quel est le meilleur assistant IA en 2026?"},
    ],
    "de": [
        {"topic": "NVIDIA GTC 2026: Die KI-Revolution", "reason": "GTC 2026 (16.-19. März)", "description": "Jensen Huang präsentiert die nächste KI-Generation"},
        {"topic": "Zeitalter der agentischen KI", "reason": "KI-Trend #1 in 2026", "description": "KI-Agenten die autonom planen und handeln"},
        {"topic": "KI-Chip-Krieg 2026", "reason": "NVIDIA vs AMD vs Intel", "description": "Wer gewinnt das KI-Halbleiter-Rennen?"},
        {"topic": "ChatGPT vs Claude 4 Vergleich", "reason": "KI-Modell-Wettbewerb", "description": "Das beste KI-Modell 2026 im Vergleich"},
        {"topic": "Jobs die KI ersetzen wird", "reason": "Automatisierungsfolgen", "description": "Welche Berufe gefährdet sind und wie man sich anpasst"},
        {"topic": "Made in Germany trifft KI", "reason": "Deutsche Industrie und KI", "description": "Wie KI die deutsche Industrie transformiert"},
    ],
    "pt": [
        {"topic": "NVIDIA GTC 2026: A Revolução da IA", "reason": "GTC 2026 (16-19 de março)", "description": "Jensen Huang apresenta a próxima geração de IA"},
        {"topic": "Era da IA Agêntica", "reason": "Tendência #1 de IA em 2026", "description": "Agentes de IA que planejam e agem de forma autônoma"},
        {"topic": "Guerra de Chips de IA 2026", "reason": "NVIDIA vs AMD vs Intel", "description": "Quem vence a corrida dos semicondutores de IA?"},
        {"topic": "ChatGPT vs Claude 4", "reason": "Competição de modelos de IA", "description": "O melhor modelo de IA de 2026 comparado"},
        {"topic": "Empregos que a IA vai substituir", "reason": "Impacto da automação", "description": "Quais carreiras estão em risco e como se adaptar"},
        {"topic": "IA no Brasil: Oportunidades 2026", "reason": "Crescimento da IA no Brasil", "description": "Como o Brasil está aproveitando a revolução da IA"},
    ],
    "ar": [
        {"topic": "ثورة NVIDIA GTC 2026 بالذكاء الاصطناعي", "reason": "مؤتمر GTC 2026 (16-19 مارس)", "description": "جنسن هوانغ يكشف عن الجيل القادم من تقنيات الذكاء الاصطناعي"},
        {"topic": "عصر الذكاء الاصطناعي الفاعل", "reason": "أبرز اتجاهات 2026", "description": "وكلاء الذكاء الاصطناعي الذين يخططون ويتصرفون باستقلالية"},
        {"topic": "حرب رقائق الذكاء الاصطناعي 2026", "reason": "NVIDIA ضد AMD ضد Intel", "description": "من سيفوز بسباق أشباه الموصلات؟"},
        {"topic": "ChatGPT ضد Claude 4 مقارنة", "reason": "تنافس نماذج الذكاء الاصطناعي", "description": "أفضل نموذج ذكاء اصطناعي في 2026"},
        {"topic": "الوظائف التي سيحل فيها الذكاء الاصطناعي", "reason": "تأثير الأتمتة", "description": "المهن المهددة وكيفية التكيف"},
        {"topic": "الذكاء الاصطناعي والعالم العربي", "reason": "النمو التقني في المنطقة", "description": "كيف تستفيد الدول العربية من ثورة الذكاء الاصطناعي"},
    ],
    "hi": [
        {"topic": "NVIDIA GTC 2026: AI क्रांति", "reason": "GTC 2026 (16-19 मार्च)", "description": "जेन्सन हुआंग ने अगली पीढ़ी की AI तकनीक पेश की"},
        {"topic": "Agentic AI का युग", "reason": "2026 का सबसे बड़ा AI ट्रेंड", "description": "स्वायत्त रूप से योजना बनाने वाले AI एजेंट"},
        {"topic": "2026 AI चिप वॉर", "reason": "NVIDIA vs AMD vs Intel", "description": "AI सेमीकंडक्टर रेस में कौन जीतेगा?"},
        {"topic": "ChatGPT vs Claude 4 तुलना", "reason": "AI मॉडल प्रतिस्पर्धा", "description": "2026 का सर्वश्रेष्ठ AI मॉडल"},
        {"topic": "AI कौन सी नौकरियां लेगा", "reason": "ऑटोमेशन का प्रभाव", "description": "कौन से करियर खतरे में हैं और कैसे अनुकूलन करें"},
        {"topic": "भारत में AI: 2026 के अवसर", "reason": "भारत की डिजिटल क्रांति", "description": "AI से भारत की अर्थव्यवस्था कैसे बदल रही है"},
    ],
    "it": [
        {"topic": "NVIDIA GTC 2026: La Rivoluzione IA", "reason": "GTC 2026 (16-19 marzo)", "description": "Jensen Huang presenta la prossima generazione di IA"},
        {"topic": "Era dell'IA Agentiva", "reason": "Trend IA #1 nel 2026", "description": "Agenti IA che pianificano e agiscono autonomamente"},
        {"topic": "Guerra dei Chip IA 2026", "reason": "NVIDIA vs AMD vs Intel", "description": "Chi vince la corsa ai semiconduttori IA?"},
        {"topic": "ChatGPT vs Claude 4", "reason": "Competizione modelli IA", "description": "Il miglior modello IA del 2026 a confronto"},
        {"topic": "Lavori che l'IA sostituirà", "reason": "Impatto dell'automazione", "description": "Quali carriere sono a rischio e come adattarsi"},
        {"topic": "IA Made in Italy", "reason": "Innovazione italiana nell'IA", "description": "Come l'Italia affronta la rivoluzione dell'intelligenza artificiale"},
    ],
    "ru": [
        {"topic": "NVIDIA GTC 2026: ИИ-революция", "reason": "GTC 2026 (16-19 марта)", "description": "Дженсен Хуанг представил новое поколение ИИ-технологий"},
        {"topic": "Эра агентного ИИ", "reason": "Главный ИИ-тренд 2026 года", "description": "ИИ-агенты, которые планируют и действуют автономно"},
        {"topic": "Война чипов ИИ 2026", "reason": "NVIDIA против AMD против Intel", "description": "Кто выиграет гонку полупроводников?"},
        {"topic": "ChatGPT против Claude 4", "reason": "Конкуренция ИИ-моделей", "description": "Лучшая ИИ-модель 2026 года"},
        {"topic": "Профессии, которые заменит ИИ", "reason": "Влияние автоматизации", "description": "Какие карьеры под угрозой и как адаптироваться"},
        {"topic": "ИИ и российские технологии", "reason": "Развитие отечественного ИИ", "description": "Как Россия развивает технологии ИИ"},
    ],
}


class TrendFinder:
    def __init__(self, lang="ko"):
        self.lang = lang
        geo_info = GEO_MAP.get(lang, GEO_MAP["en"])
        self.geo, self.hl, self.region = geo_info

    def get_trends(self, limit=5):
        """여러 소스에서 트렌드 수집, 최적 주제 리스트 반환"""
        # 1차: Google Trends
        if PYTRENDS_AVAILABLE:
            try:
                trends = self._google_trends(limit)
                if trends:
                    return trends
            except Exception as e:
                print(f"   [warn] Google Trends error: {e}")

        # 2차: fallback
        return self._default_trends(limit)

    def _google_trends(self, limit):
        pytrends = TrendReq(hl=self.hl, tz=0)
        df = pytrends.trending_searches(pn=self.region)
        results = []
        for _, row in df.head(limit).iterrows():
            keyword = str(row[0])
            results.append({
                "topic": keyword,
                "reason": f"Google Trends rising — {self.region}",
                "description": f"'{keyword}' is trending on Google in {self.region}.",
                "source": "google_trends",
            })
        return results

    def _default_trends(self, limit):
        """언어별 기본 트렌드 목록"""
        topics = DEFAULT_TOPICS.get(self.lang, DEFAULT_TOPICS["en"])
        return topics[:limit]
