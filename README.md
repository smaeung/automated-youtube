# 🎬 Automated YouTube Shorts Creator

자동으로 트렌드를 탐색하고 YouTube Shorts 영상을 제작하는 AI 파이프라인 프로그램입니다.

> **Powered by Claude AI + edge-tts + moviepy + Pillow**

---

## ✨ 주요 기능

| 기능 | 설명 |
|------|------|
| 🔍 자동 트렌드 탐색 | Google Trends (Korea) 기반 최신 트렌드 자동 감지 |
| 🤖 AI 스크립트 생성 | Claude AI가 구조화된 JSON 스크립트 자동 생성 |
| 🖼 슬라이드 이미지 | PIL로 1080×1920 (9:16) 전문적인 슬라이드 제작 |
| 🌐 웹 배경 이미지 | DuckDuckGo 검색으로 주제에 맞는 배경 이미지 자동 다운로드 |
| 🔊 고품질 TTS | edge-tts 한국어/영어 자연스러운 음성 합성 |
| 🎬 자막 오버레이 | 영상에 실시간 자막이 표시되는 MP4 최종 출력 |

---

## 🚀 시작하기

### 1. 환경 요구사항

- Python 3.9 이상
- Windows 10/11 권장 (한국어 폰트 기본 탑재)
- [FFmpeg](https://ffmpeg.org/) (imageio-ffmpeg가 자동 설치)

### 2. 설치

```bash
# 저장소 클론
git clone https://github.com/smaeung/automated-youtube.git
cd automated-youtube

# 가상환경 생성 및 활성화 (권장)
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Windows CMD
.\.venv\Scripts\activate.bat
# Git Bash / macOS / Linux
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. API 키 설정

```bash
# .env.example 파일을 .env로 복사
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
```

`.env` 파일을 열고 Anthropic API 키를 입력하세요:

```env
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

> 🔑 API 키는 [Anthropic Console](https://console.anthropic.com/)에서 발급받을 수 있습니다.

---

## 📖 사용법

### 기본 사용 (자동 트렌드 탐색 → 영상 제작)

```bash
python auto_video.py
```

### 주제 직접 지정

```bash
python auto_video.py --topic "GTC 2026"
python auto_video.py --topic "AI 에이전트"
```

### 트렌드 목록만 확인

```bash
python auto_video.py --list-trends
```

### 스크립트만 생성 (영상 제작 없이)

```bash
python auto_video.py --topic "AI 트렌드" --no-video
```

### 옵션 전체 목록

```
옵션              기본값    설명
--topic TEXT     (자동)    영상 주제 직접 지정
--slides N       8         슬라이드 수
--duration       5min      영상 길이 (1min/3min/5min/10min)
--voice          male      TTS 목소리 (male/female)
--lang           ko        언어 (ko/en)
--output DIR     output    출력 디렉토리
--list-trends              트렌드 TOP 10 목록 출력
--no-video                 스크립트만 생성 (영상 X)
```

---

## 🗂 프로젝트 구조

```
automated-youtube/
├── auto_video.py           # 🚀 메인 CLI 진입점
├── requirements.txt        # 의존성 목록
├── .env.example            # 환경 변수 예제 (API 키)
├── README.md
│
├── modules/
│   ├── __init__.py
│   ├── trend_finder.py     # 🔍 트렌드 탐색 (pytrends + fallback)
│   ├── script_gen.py       # 🤖 Claude AI 스크립트 생성
│   ├── image_search.py     # 🌐 DuckDuckGo 이미지 검색 & 다운로드
│   ├── slide_maker.py      # 🖼 PIL 슬라이드 이미지 생성 (1080×1920)
│   ├── tts_engine.py       # 🔊 edge-tts TTS 음성 생성
│   └── video_builder.py    # 🎬 moviepy 영상 조립 + 자막
│
└── output/                 # 📁 생성된 파일 저장
    ├── script_YYYYMMDD_HHMMSS.json
    ├── slides_YYYYMMDD_HHMMSS/
    ├── audio_YYYYMMDD_HHMMSS/
    └── {topic}_YYYYMMDD_HHMMSS.mp4
```

---

## ⚙️ 파이프라인 단계

```
STEP 1  🔍  트렌드 탐색      Google Trends KR → 자동 주제 선택
STEP 2  🤖  스크립트 생성    Claude API → 구조화된 JSON (제목, 태그, 슬라이드)
STEP 3  🌐  배경 이미지 검색  DuckDuckGo → 주제별 고품질 사진 다운로드
STEP 4  🖼  슬라이드 생성    PIL 1080×1920 이미지 + 배경/텍스트/아이콘
STEP 5  🔊  TTS 음성 생성   edge-tts → 각 슬라이드별 MP3 파일
STEP 6  🎬  영상 조립 + 자막 moviepy → 자막 오버레이 최종 MP4 출력
```

---

## 🎨 슬라이드 디자인

- **해상도**: 1080×1920 (9:16 YouTube Shorts)
- **폰트**: Malgun Gothic Bold (Windows 기본 탑재)
- **색상**: NVIDIA Green (#76B900) + 딥 블랙 (#000000)
- **구성 요소**: 헤드라인 · 서브 헤드라인 · 통계 박스 · 칩 뱃지 · 자막 바

---

## 🔊 TTS 음성 목록

| 언어 | 성별   | 음성 모델              |
|------|--------|------------------------|
| 한국어 | 남성 | ko-KR-InJoonNeural     |
| 한국어 | 여성 | ko-KR-SunHiNeural      |
| 영어   | 남성 | en-US-GuyNeural        |
| 영어   | 여성 | en-US-JennyNeural      |

---

## 📦 의존성

```
anthropic>=0.40.0         Claude AI API
edge-tts>=6.1.9           Microsoft 무료 TTS
moviepy>=1.0.3,<2.0.0     영상 편집
imageio-ffmpeg>=0.4.9     FFmpeg 자동 설치
Pillow>=10.0.0            이미지 처리
pytrends>=4.9.2           Google Trends API
requests>=2.31.0          HTTP 요청
python-dotenv>=1.0.0      환경 변수 관리
numpy>=1.24.0             배열 처리
duckduckgo-search>=6.0.0  이미지 검색 (무료, API 불필요)
```

---

## 🛠 트러블슈팅

### Windows 한국어 인코딩 오류
```bash
# 환경 변수 설정 후 실행
set PYTHONIOENCODING=utf-8
python auto_video.py
```

### pytrends 연결 오류
트렌드 탐색에 실패해도 내장된 최신 토픽 목록으로 자동 대체됩니다.

### duckduckgo-search 미설치 시
```
[skip] duckduckgo-search 미설치 — 기본 배경 사용
```
배경 이미지 없이 그라디언트 배경으로 슬라이드를 생성합니다.

### moviepy 설치 오류
```bash
pip install "moviepy>=1.0.3,<2.0.0" imageio-ffmpeg
```

---

## 📄 라이선스

MIT License

---

## 🙏 사용 기술

- [Anthropic Claude](https://anthropic.com) - AI 스크립트 생성
- [edge-tts](https://github.com/rany2/edge-tts) - Microsoft TTS
- [MoviePy](https://zulko.github.io/moviepy/) - Python 영상 편집
- [Pillow](https://pillow.readthedocs.io/) - 이미지 처리
- [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search) - 무료 이미지 검색
