"""
DuckDuckGo 이미지 검색 + 다운로드 모듈
각 슬라이드 키워드로 고품질 배경 이미지를 가져옵니다.
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import requests
from pathlib import Path

try:
    from duckduckgo_search import DDGS
    DDG_AVAILABLE = True
except ImportError:
    DDG_AVAILABLE = False

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}


class ImageSearcher:
    def __init__(self):
        if not DDG_AVAILABLE:
            print("   [warn] duckduckgo-search 미설치 — 배경 이미지 없이 진행합니다.")
            print("          설치: pip install duckduckgo-search")

    @property
    def available(self):
        return DDG_AVAILABLE

    def search(self, query, output_path, max_tries=10):
        """
        키워드로 이미지 검색 후 첫 번째 성공 이미지를 다운로드.
        반환: 저장된 경로(str) 또는 None(실패 시)
        """
        if not DDG_AVAILABLE:
            return None

        # 검색 쿼리에 고품질 키워드 추가
        full_query = f"{query} technology photo 4K"
        try:
            ddgs = DDGS()
            results = list(ddgs.images(
                keywords=full_query,
                max_results=max_tries,
                type_image="photo",
                size="large",
            ))
        except Exception as e:
            print(f"   [warn] 이미지 검색 실패: {e}")
            return None

        for r in results:
            url = r.get("image", "")
            if not url or not url.startswith("http"):
                continue
            try:
                resp = requests.get(url, timeout=6, headers=HEADERS)
                # 최소 20KB 이상인 이미지만 사용 (아이콘/썸네일 제외)
                if resp.status_code == 200 and len(resp.content) > 20_000:
                    out = Path(output_path)
                    out.write_bytes(resp.content)
                    # 유효한 이미지인지 PIL로 검증
                    from PIL import Image as PILImage
                    PILImage.open(out).verify()
                    return str(out)
            except Exception:
                # 손상된 이미지나 다운로드 실패 → 다음 시도
                try:
                    Path(output_path).unlink(missing_ok=True)
                except Exception:
                    pass
                continue

        return None
