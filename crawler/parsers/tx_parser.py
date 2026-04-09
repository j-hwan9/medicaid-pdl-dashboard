import pdfplumber
import io
import time

TARGET_DRUGS = {
    "adalimumab": ["adalimumab", "hadlima", "humira", "hyrimoz", "cyltezo", "yuflyma", "abrilada"],
    "ustekinumab": ["ustekinumab", "stelara", "wezlana", "otulfi"],
}

LANDING_URL = "https://www.txvendordrug.com/formulary/preferred-drugs"
BASE_URL    = "https://www.txvendordrug.com"


def _find_and_download_pdf():
    """
    Playwright로 랜딩 페이지 방문 → 최신 PDF 링크 동적 탐색 → 다운로드
    URL 하드코딩 안 함 → 날짜 기반 파일명 변경에 자동 대응
    """
    from playwright.sync_api import sync_playwright

    print("[TX] Launching Playwright browser...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )
        page = context.new_page()

        # 1단계: 랜딩 페이지에서 최신 PDF 링크 탐색
        print(f"[TX] Visiting: {LANDING_URL}")
        page.goto(LANDING_URL, wait_until="networkidle", timeout=30000)
        time.sleep(2)

        pdf_url = None

        # <a href="...preferred-drug-list.pdf"> 패턴으로 탐색
        links = page.query_selector_all("a[href]")
        for link in links:
            href = link.get_attribute("href") or ""
            if "preferred-drug-list" in href and href.endswith(".pdf"):
                pdf_url = href if href.startswith("http") else BASE_URL + href
                print(f"[TX] Found PDF link: {pdf_url}")
                break

        if not pdf_url:
            raise ValueError("PDF link not found on landing page — site structure may have changed")

        # 2단계: PDF 다운로드 — page.goto() 아닌 context.request로 직접 GET
        # (Playwright는 PDF를 "다운로드"로 인식해서 goto()가 막힘)
        print(f"[TX] Downloading: {pdf_url}")
        response = context.request.get(
            pdf_url,
            headers={"Referer": LANDING_URL},
            timeout=60000,
        )
        if response.status != 200:
            raise ValueError(f"PDF download failed: HTTP {response.status}")

        pdf_bytes = response.body()
        print(f"[TX] Downloaded: {len(pdf_bytes):,} bytes")

        browser.close()
        return pdf_bytes


def _parse_pdf(content):
    """extract_tables() 기반 파싱 — 페이지 텍스트 덤프보다 정확"""
    results = {
        drug: {"status": "not_found", "detail": "", "brands": [], "pa_required": None, "is_sb": False}
        for drug in TARGET_DRUGS
    }

    with pdfplumber.open(io.BytesIO(content)) as pdf:
        print(f"[TX] Parsing {len(pdf.pages)} pages...")

        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row:
                        continue
                    cells    = [str(c).strip().lower() if c else "" for c in row]
                    row_text = " ".join(cells)

                    for drug_key, aliases in TARGET_DRUGS.items():
                        if any(alias in row_text for alias in aliases):
                            if "non-preferred" in row_text or "nonpreferred" in row_text:
                                status = "non-preferred"
                            elif "preferred" in row_text:
                                status = "preferred"
                            else:
                                status = "unknown"

                            pa    = "PA Required" if any(c == "pa" for c in cells) else "No PA"
                            brand = cells[0].title() if cells[0] else ""

                            print(f"[TX] {drug_key} → {status} (page {page_num + 1})")

                            results[drug_key] = {
                                "status":     status,
                                "detail":     f"Page {page_num + 1}",
                                "brands":     results[drug_key]["brands"] + ([brand] if brand else []),
                                "pa_required": pa,
                                "is_sb":      True,
                            }

    return results


def get_tx_data(base_url=None):
    """pipeline.py 호출용 메인 함수"""
    try:
        content = _find_and_download_pdf()
        results = _parse_pdf(content)
        print(f"[TX] Complete: {results}")
        return results
    except Exception as e:
        print(f"[TX] FAILED: {e}")
        return {
            drug: {"status": "error", "detail": str(e), "is_sb": False}
            for drug in TARGET_DRUGS
        }


if __name__ == "__main__":
    import json
    print(json.dumps(get_tx_data(), indent=2, ensure_ascii=False))
