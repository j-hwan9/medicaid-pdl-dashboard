import requests
import pdfplumber
import io
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 찾을 약물 목록 (확장 가능)
TARGET_DRUGS = {
    "adalimumab": ["adalimumab", "hadlima", "humira", "hyrimoz", "cyltezo", "yuflyma", "abrilada"],
    "ustekinumab": ["ustekinumab", "stelara", "wezlana", "otulfi"],
}

DIRECT_PDF_URL = "https://www.txvendordrug.com/sites/default/files/docs/formulary/pdl-criteria-tables/pdl-table.pdf"
BASE_URL = "https://www.txvendordrug.com"

def _make_session():
    """재시도 전략 포함 세션 생성"""
    session = requests.Session()
    retry = Retry(
        total=4,
        backoff_factor=2,          # 1s → 2s → 4s → 8s
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session

def _get_headers(referer=None):
    """실제 Chrome과 동일한 헤더셋"""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none" if not referer else "same-origin",
        "Sec-Fetch-User": "?1",
        **({"Referer": referer} if referer else {}),
    }

def _download_pdf(session):
    """
    1단계: 홈페이지 접속으로 쿠키 선획득
    2단계: PDF 직접 다운로드
    """
    print("[TX] Step 1: Seeding cookies via homepage...")
    try:
        session.get(BASE_URL, headers=_get_headers(), timeout=15)
        time.sleep(2)  # 사람처럼 대기
    except Exception as e:
        print(f"[TX] Homepage seed failed (non-fatal): {e}")

    print(f"[TX] Step 2: Downloading PDF from {DIRECT_PDF_URL}")
    pdf_headers = _get_headers(referer=BASE_URL + "/formulary/prior-authorization/preferred-drugs")
    pdf_headers["Accept"] = "application/pdf,application/octet-stream,*/*"
    pdf_headers["Sec-Fetch-Dest"] = "document"

    response = session.get(DIRECT_PDF_URL, headers=pdf_headers, timeout=40)
    response.raise_for_status()

    # PDF 맞는지 확인 (봇 차단 시 HTML 반환하는 경우 있음)
    content_type = response.headers.get("Content-Type", "")
    if "html" in content_type:
        raise ValueError(f"Got HTML instead of PDF — likely bot-blocked. Content-Type: {content_type}")

    print(f"[TX] PDF downloaded: {len(response.content):,} bytes")
    return response.content

def _parse_pdf(content):
    """
    extract_tables() 기반 정확한 파싱
    텍스트 덤프 대신 행/열 구조로 약물명 + 상태 추출
    """
    results = {drug: {"status": "not_found", "detail": "", "brands": [], "pa_required": None} 
               for drug in TARGET_DRUGS}

    with pdfplumber.open(io.BytesIO(content)) as pdf:
        print(f"[TX] Total pages: {len(pdf.pages)}")
        
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            if not tables:
                continue

            for table in tables:
                for row in table:
                    if not row:
                        continue
                    # None 셀 처리 후 소문자 변환
                    cells = [str(cell).strip().lower() if cell else "" for cell in row]
                    row_text = " ".join(cells)

                    for drug_key, aliases in TARGET_DRUGS.items():
                        if any(alias in row_text for alias in aliases):
                            # PDL 상태 판단
                            if "non-preferred" in row_text or "nonpreferred" in row_text:
                                status = "non-preferred"
                            elif "preferred" in row_text:
                                status = "preferred"
                            else:
                                status = "unknown"

                            # PA 조건 확인
                            pa = "PA Required" if "pa" in cells or any("pa" == c for c in cells) else "No PA"

                            # 브랜드명 추출 (첫 번째 셀이 보통 브랜드명)
                            brand = cells[0].title() if cells[0] else ""

                            print(f"[TX] Found '{drug_key}' on page {page_num+1}: status={status}, row={cells[:4]}")

                            results[drug_key] = {
                                "status": status,
                                "detail": f"Page {page_num+1}",
                                "brands": results[drug_key]["brands"] + ([brand] if brand else []),
                                "pa_required": pa,
                                "is_sb": True,
                            }

    return results

def get_tx_data(base_url=None):
    """
    pipeline.py에서 호출하는 메인 함수
    Returns: dict {drug_name: {status, detail, is_sb, pa_required}}
    """
    session = _make_session()
    try:
        content = _download_pdf(session)
        results = _parse_pdf(content)
        print(f"[TX] Parse complete: {results}")
        return results

    except Exception as e:
        print(f"[TX] FAILED: {e}")
        return {
            drug: {"status": "error", "detail": str(e), "is_sb": False}
            for drug in TARGET_DRUGS
        }


# 로컬 테스트용
if __name__ == "__main__":
    data = get_tx_data()
    import json
    print(json.dumps(data, indent=2, ensure_ascii=False))
