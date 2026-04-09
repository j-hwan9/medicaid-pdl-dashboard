import requests
import pdfplumber
import io
from bs4 import BeautifulSoup

def get_tx_data(base_url):
    print(f"[TX Parser] Attempting to bypass security at: {base_url}")
    
    # 서버를 속이기 위한 가짜 브라우저 정보 (User-Agent)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/'
    }

    try:
        # 1. 세션을 유지하며 접속 (사람처럼 보이게 함)
        session = requests.Session()
        response = session.get(base_url, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_link = ""
        
        # 안내 페이지에서 PDF 링크 검색
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'pdl-table' in href or 'Preferred-Drug-List' in href:
                pdf_link = href if href.startswith('http') else "https://www.txvendordrug.com" + href
                break
        
        if not pdf_link:
            print("[TX Parser] Failed to find dynamic link, using fallback.")
            pdf_link = "https://www.txvendordrug.com/sites/default/files/docs/formulary/pdl-criteria-tables/pdl-table.pdf"

        # 2. PDF 다운로드 (여기서도 headers를 보내야 함)
        print(f"[TX Parser] Downloading PDF: {pdf_link}")
        pdf_res = session.get(pdf_link, headers=headers, timeout=30)
        pdf_res.raise_for_status()
        
        # 3. PDF 내용 분석 (Adalimumab 찾기)
        with pdfplumber.open(io.BytesIO(pdf_res.content)) as pdf:
            # 텍사스는 보통 앞쪽 30페이지 내에 중요한 표가 있습니다.
            for page in pdf.pages[:30]:
                text = page.extract_text()
                if text and "Adalimumab" in text:
                    # 'Preferred' 글자가 근처에 있는지 확인
                    status = "preferred" if "Preferred" in text else "non-preferred"
                    detail = "Exclusive" if "Exclusive" in text else "Preferred"
                    return {"status": status, "detail": detail, "is_sb": True}
        
        return {"status": "non-preferred", "detail": "Not found in PDF", "is_sb": False}

    except Exception as e:
        print(f"[TX Parser] Failed: {e}")
        # 실패하더라도 파이프라인이 멈추지 않게 에러 정보를 반환
        return {"status": "error", "detail": str(e), "is_sb": False}
