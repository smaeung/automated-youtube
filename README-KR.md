# 자동 YouTube Shorts 영상 제작기

> **Claude AI · edge-tts · moviepy · Pillow 기반**

트렌드를 자동 탐색하고, AI 스크립트를 생성하며, 슬라이드 이미지와 음성을 합성해 YouTube Shorts MP4를 완성하는 AI 파이프라인입니다. **12개 언어**를 지원합니다.

**언어:** **한국어** · [English (영어)](README-EN.md)

---

## 샘플 슬라이드

**한국어** (`--lang ko`) · 주제: *"NVIDIA GTC 2026 AI 혁명"*

<table>
  <tr>
    <td><img src="docs/sample_slide_01.png" width="190"/></td>
    <td><img src="docs/sample_slide_02.png" width="190"/></td>
    <td><img src="docs/sample_slide_03.png" width="190"/></td>
    <td><img src="docs/sample_slide_04.png" width="190"/></td>
  </tr>
  <tr>
    <td align="center">HOOK</td>
    <td align="center">INTRO</td>
    <td align="center">CORE</td>
    <td align="center">CORE</td>
  </tr>
</table>

**영어** (`--lang en`) · 주제: *"NVIDIA GTC 2026: The AI Revolution"*

<table>
  <tr>
    <td><img src="docs/sample_en_slide_01.png" width="190"/></td>
    <td><img src="docs/sample_en_slide_02.png" width="190"/></td>
    <td><img src="docs/sample_en_slide_03.png" width="190"/></td>
    <td><img src="docs/sample_en_slide_04.png" width="190"/></td>
  </tr>
  <tr>
    <td align="center">HOOK</td>
    <td align="center">INTRO</td>
    <td align="center">CORE</td>
    <td align="center">CORE</td>
  </tr>
</table>

- **해상도**: 1080×1920 (9:16)
- **디자인**: NVIDIA Green `#76B900` + 딥 블랙
- **구성**: Section 태그 · 이모지 아이콘 · 헤드라인 · 통계 박스 · 칩 뱃지 · VO 스크립트 박스

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| 트렌드 자동 탐색 | Google Trends (국가별) — 최신 인기 주제 자동 선택 |
| AI 스크립트 생성 | Claude가 대상 언어로 구조화된 JSON 슬라이드 스크립트 생성 |
| 슬라이드 이미지 생성 | PIL로 1080×1920 (9:16) 전문 슬라이드 제작 |
| 배경 이미지 자동 검색 | DuckDuckGo로 주제에 맞는 고화질 사진 다운로드 |
| 고품질 TTS 음성 | edge-tts — 12개 언어 자연스러운 음성 합성 |
| 자막 오버레이 영상 | moviepy로 자막이 포함된 최종 MP4 출력 |
| 12개 언어 지원 | `ko` `en` `ja` `zh` `es` `fr` `de` `pt` `ar` `hi` `it` `ru` |

---

## 요구사항

- Python 3.9 이상
- Windows 10/11 권장 (한/중/일 폰트 기본 탑재)
- FFmpeg — `imageio-ffmpeg`가 자동 설치
- [Anthropic API 키](https://console.anthropic.com/)

---

## 설치

```bash
# 1. 클론
git clone https://github.com/smaeung/automated-youtube.git
cd automated-youtube

# 2. 가상환경 생성 (권장)
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Windows CMD
.\.venv\Scripts\activate.bat
# Git Bash / macOS / Linux
source .venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. API 키 설정
copy .env.example .env      # Windows
cp   .env.example .env      # macOS / Linux
```

`.env` 파일을 열어 API 키를 입력합니다:

```env
ANTHROPIC_API_KEY=sk-ant-여기에-키-입력
```

> 🔑 API 키는 [Anthropic Console](https://console.anthropic.com/)에서 발급받을 수 있습니다.

---

## 사용법

### 기본 실행 (자동 트렌드 탐색 → 영상 제작)

```bash
python auto_video.py
```

### 주제 직접 지정

```bash
python auto_video.py --topic "GPT-5 vs Claude 4"
python auto_video.py --topic "2026 AI 반도체 전쟁"
```

### 언어 선택

```bash
python auto_video.py --lang ko          # 한국어 (기본값)
python auto_video.py --lang en          # 영어
python auto_video.py --lang ja          # 일본어
python auto_video.py --lang zh          # 중국어 (간체)
python auto_video.py --lang es          # 스페인어
python auto_video.py --lang fr          # 프랑스어
python auto_video.py --lang de          # 독일어
python auto_video.py --lang pt          # 포르투갈어 (브라질)
python auto_video.py --lang ar          # 아랍어
python auto_video.py --lang hi          # 힌디어
python auto_video.py --lang it          # 이탈리아어
python auto_video.py --lang ru          # 러시아어
```

### 스크립트만 생성 (영상 제작 없이)

```bash
python auto_video.py --topic "AI 에이전트" --lang ko --no-video
```

### 트렌드 목록 확인

```bash
python auto_video.py --lang ja --list-trends   # 일본 트렌드 TOP 10
python auto_video.py --lang en --list-trends   # 미국 트렌드 TOP 10
```

### 전체 옵션

```
옵션               기본값    설명
--topic TEXT      (자동)    영상 주제 직접 지정
--slides N        8         슬라이드 수
--duration        5min      영상 길이: 1min / 3min / 5min / 10min
--voice           male      TTS 목소리: male / female
--lang            ko        출력 언어 코드
--output DIR      output    출력 디렉토리
--list-trends               트렌드 TOP 10 출력 후 종료
--no-video                  스크립트만 생성 (영상 X)
```

---

## 지원 언어 및 TTS 음성

| 코드 | 언어 | 남성 음성 | 여성 음성 |
|------|------|-----------|-----------|
| `ko` | 한국어 | ko-KR-InJoonNeural | ko-KR-SunHiNeural |
| `en` | 영어 | en-US-GuyNeural | en-US-JennyNeural |
| `ja` | 일본어 | ja-JP-KeitaNeural | ja-JP-NanamiNeural |
| `zh` | 중국어 | zh-CN-YunjianNeural | zh-CN-XiaoxiaoNeural |
| `es` | 스페인어 | es-ES-AlvaroNeural | es-ES-ElviraNeural |
| `fr` | 프랑스어 | fr-FR-HenriNeural | fr-FR-DeniseNeural |
| `de` | 독일어 | de-DE-ConradNeural | de-DE-KatjaNeural |
| `pt` | 포르투갈어(BR) | pt-BR-AntonioNeural | pt-BR-FranciscaNeural |
| `ar` | 아랍어 | ar-SA-HamedNeural | ar-SA-ZariyahNeural |
| `hi` | 힌디어 | hi-IN-MadhurNeural | hi-IN-SwaraNeural |
| `it` | 이탈리아어 | it-IT-DiegoNeural | it-IT-ElsaNeural |
| `ru` | 러시아어 | ru-RU-DmitryNeural | ru-RU-SvetlanaNeural |

---

## 프로젝트 구조

```
automated-youtube/
├── auto_video.py            # 메인 CLI 진입점
├── requirements.txt         # 의존성 목록
├── .env.example             # API 키 예제
├── README.md                # 언어 선택 인덱스
├── README-EN.md             # 영어 문서
├── README-KR.md             # 이 파일
│
└── modules/
    ├── trend_finder.py      # Google Trends (국가별) + 언어별 fallback 목록
    ├── script_gen.py        # Claude AI — 대상 언어로 JSON 스크립트 생성
    ├── image_search.py      # DuckDuckGo 이미지 검색 & 다운로드
    ├── slide_maker.py       # PIL 1080×1920 슬라이드 — 언어별 폰트 자동 선택
    ├── tts_engine.py        # edge-tts — 12개 언어 음성 맵
    └── video_builder.py     # moviepy — 슬라이드 + 오디오 + 자막 → MP4
```

---

## 파이프라인

```
STEP 1  트렌드 탐색   Google Trends (언어별 국가) → 최적 주제 선택
STEP 2  스크립트 생성  Claude API → 구조화된 JSON (제목·태그·슬라이드)
STEP 3  배경 이미지   DuckDuckGo → 주제별 고화질 배경 사진 다운로드
STEP 4  슬라이드 생성  PIL 1080×1920 → slide_01.png … slide_N.png
STEP 5  TTS 음성 생성  edge-tts → audio_01.mp3 … audio_N.mp3
STEP 6  영상 조립     moviepy → 자막 오버레이 → {topic}_YYYYMMDD.mp4
```

---

## 슬라이드 디자인

- **해상도**: 1080×1920 (9:16 YouTube Shorts)
- **색상**: NVIDIA Green `#76B900` + 딥 블랙 `#000000`
- **폰트**: 언어별 자동 선택
  - 한/중/일 → 맑은 고딕 / YuGothic / 微软雅黑 (시스템 기본)
  - 라틴(EN·ES·FR·DE·PT·IT) → Arial Bold
  - 아랍어 → ArabType / Arial
  - 힌디어 → Nirmala UI
  - 러시아어 → Arial (키릴 문자 지원)
- **구성 요소**: Section 태그 · 아이콘 · 헤드라인 · 서브 헤드라인 · 통계 박스 · 칩 뱃지 · VO 스크립트 박스

---

## 트러블슈팅

### Windows 인코딩 오류

```bash
set PYTHONIOENCODING=utf-8
python auto_video.py
```

### pytrends 연결 실패

언어별로 내장된 최신 토픽 목록으로 자동 대체됩니다. 별도 조치 불필요.

### 배경 이미지 미사용

```
[skip] duckduckgo-search not installed — using gradient background
```

설치: `pip install duckduckgo-search`
미설치 시 그라디언트 배경으로 자동 전환.

### 아랍어 슬라이드 렌더링 제한

PIL이 RTL(우→좌) 텍스트를 네이티브로 지원하지 않아 슬라이드에서 아랍어가 좌→우 순으로 표시됩니다. TTS 음성은 정상 동작합니다.
완전한 RTL 지원을 원하면 `arabic-reshaper` + `python-bidi` 패키지를 추가로 설치하세요.

### moviepy 설치 오류

```bash
pip install "moviepy>=1.0.3,<2.0.0" imageio-ffmpeg
```

---

## 의존성

```
anthropic>=0.40.0         Claude AI API
edge-tts>=6.1.9           Microsoft 무료 TTS (12개 언어)
moviepy>=1.0.3,<2.0.0     영상 편집
imageio-ffmpeg>=0.4.9     FFmpeg 자동 설치
Pillow>=10.0.0            이미지 처리
pytrends>=4.9.2           Google Trends API
requests>=2.31.0          HTTP 요청
python-dotenv>=1.0.0      환경 변수 관리
numpy>=1.24.0             배열 처리
duckduckgo-search>=6.0.0  무료 이미지 검색 (API 키 불필요)
```

---

## 라이선스

MIT License

---

## 사용 기술

- [Anthropic Claude](https://anthropic.com) — AI 스크립트 생성
- [edge-tts](https://github.com/rany2/edge-tts) — Microsoft Neural TTS
- [MoviePy](https://zulko.github.io/moviepy/) — Python 영상 편집
- [Pillow](https://pillow.readthedocs.io/) — 이미지 처리
- [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search) — 무료 이미지 검색
