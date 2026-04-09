import pdfplumber
import io
import os
import time

# 찾을 약물 목록
TARGET_DRUGS = {
    "adalimumab": ["adalimumab", "hadlima", "humira", "hyrimoz", "cyltezo", "yuflyma", "abrilada"],
    "ustekinumab": ["ustekinumab", "stelara", "wezlana", "otulfi"],
}

DIRECT_PDF_URL = "https://www.txvendordrug.com/sites/default/files/docs/formulary/pdl-criteria-tables/pdl-table.pdf"
LANDING_URL = "https://www.txvendordrug.com/formulary/prior-authorization/preferred-drugs"

def _download_pdf_playwright():
    """
    Playwright로 실제 브라우저 실행 → PDF 바이트 반환
    GitHub Actions IP 차단을 진짜 브라우저로 우회
    """
    from playwright.sync_api import sync_playwright

    print("[TX] Launching Playwright browser...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',  # GitHub Actions 메모리 제한 대응
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )

        page = context.new_page()

        # 1단계: 랜딩 페이지 방문 → 쿠키/세션 획득
        print(f"[TX] Visiting landing page: {LANDING_URL}")
        page.goto(LANDING_URL, wait_until="networkidle", timeout=30000)
        time.sleep(2)

        # 2단계: PDF를 response 인터셉트로 다운로드
        print(f"[TX] Downloading PDF: {DIRECT_PDF_URL}")
        pdf_bytes = None

        with page.expect_response(
            lambda r: "pdl-table" in r.url or r.url.endswith(".pdf"),
            timeout=40000
        ) as response_info:
            page.goto(DIRECT_PDF_URL, timeout=40000)

        response = response_info.value
        if response.status != 200:
            raise ValueError(f"PDF download failed: HTTP {response.status}")

        pdf_bytes = response.body()
        print(f"[TX] PDF downloaded via Playwright: {len(pdf_bytes):,} bytes")

        browser.close()
        return pdf_bytes


def _parse_pdf(content):
    """
    extract_tables() 기반 정확한 파싱
    텍스트 덤프 대신 행/열 구조로 약물명 + 상태 추출
    """
    results = {
        drug: {"status": "not_found", "detail": "", "brands": [], "pa_required": None}
        for drug in TARGET_DRUGS
    }

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
                    cells = [str(cell).strip().lower() if cell else "" for cell in row]
                    row_text = " ".join(cells)

                    for drug_key, aliases in TARGET_DRUGS.items():
                        if any(alias in row_text for alias in aliases):
                            if "non-preferred" in row_text or "nonpreferred" in row_text:
                                status = "non-preferred"
                            elif "preferred" in row_text:
                                status = "preferred"
                            else:
                                status = "unknown"

                            pa = "PA Required" if any(c == "pa" for c in cells) else "No PA"
                            brand = cells[0].title() if cells[0] else ""

                            print(f"[TX] Found '{drug_key}' on page {page_num+1}: status={status}")

                            results[drug_key] = {
                                "status": status,
                                "detail": f"Page {page_num + 1}",
                                "brands": results[drug_key]["brands"] + ([brand] if brand else []),
                                "pa_required": pa,
                                "is_sb": True,
                            }

    return results


def get_tx_data(base_url=None):
    """pipeline.py에서 호출하는 메인 함수"""
    try:
        content = _download_pdf_playwright()
        results = _parse_pdf(content)
        print(f"[TX] Parse complete: {results}")
        return results
    except Exception as e:
        print(f"[TX] FAILED: {e}")
        return {
            drug: {"status": "error", "detail": str(e), "is_sb": False}
            for drug in TARGET_DRUGS
        }


if __name__ == "__main__":
    import json
    data = get_tx_data()
    print(json.dumps(data, indent=2, ensure_ascii=False))
