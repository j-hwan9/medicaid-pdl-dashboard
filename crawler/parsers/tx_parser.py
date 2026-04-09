import requests
import pdfplumber
import io
from bs4 import BeautifulSoup

def get_tx_data(base_url):
    print(f"[TX Parser] Finding PDF link from: {base_url}")
    
    try:
        # 1. 안내 페이지에서 실제 PDF 링크 찾아내기
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 'pdl-table.pdf'가 포함된 링크 찾기
        pdf_link = ""
        for link in soup.find_all('a', href=True):
            if 'pdl-table.pdf' in link['href']:
                pdf_link = link['href']
                if not pdf_link.startswith('http'):
                    pdf_link = "https://www.txvendordrug.com" + pdf_link
                break
        
        if not pdf_link:
            # 못 찾을 경우 예비 주소 시도
            pdf_link = "https://www.txvendordrug.com/sites/default/files/docs/formulary/pdl-criteria-tables/pdl-table.pdf"

        print(f"[TX Parser] Downloading PDF from: {pdf_link}")
        
        # 2. PDF 다운로드 및 분석
        pdf_res = requests.get(pdf_link, timeout=20)
        pdf_res.raise_for_status()
        
        with pdfplumber.open(io.BytesIO(pdf_res.content)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text and "Adalimumab" in text:
                    # 간단한 예시 로직 (실제 표 구조에 따라 정밀화 필요)
                    if "Preferred" in text:
                        return {"adalimumab": {"status": "preferred", "detail": "Exclusive/Preferred", "is_sb": True}}
        
        return {"adalimumab": {"status": "non-preferred", "detail": "Not found in PDF", "is_sb": False}}

    except Exception as e:
        print(f"[TX Parser] Error: {e}")
        raise e
