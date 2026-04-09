import requests
import pdfplumber
import io
from bs4 import BeautifulSoup

def get_tx_data(base_url):
    print(f"[TX Parser] Start searching at: {base_url}")
    
    try:
        # 1. 안내 페이지 접속
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(base_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 2. PDF 링크 낚아채기
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_link = ""
        
        # 'Preferred Drug List'나 'pdl-table'이 포함된 링크를 찾습니다.
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'pdl-table' in href or 'Preferred-Drug-List' in href:
                pdf_link = href if href.startswith('http') else "https://www.txvendordrug.com" + href
                break
        
        if not pdf_link:
            # 주소를 못 찾았을 때를 대비한 최후의 보루 (2026년 4월 기준 유효 확인 필요)
            pdf_link = "https://www.txvendordrug.com/sites/default/files/docs/formulary/pdl-criteria-tables/pdl-table.pdf"

        print(f"[TX Parser] Target PDF found: {pdf_link}")
        
        # 3. PDF 다운로드 및 데이터 추출
        pdf_res = requests.get(pdf_link, headers=headers, timeout=20)
        pdf_res.raise_for_status()
        
        with pdfplumber.open(io.BytesIO(pdf_res.content)) as pdf:
            # 텍사스 PDL은 양이 많으므로 앞쪽 페이지 위주로 검색
            for page in pdf.pages[:50]: 
                text = page.extract_text()
                if text and "Adalimumab" in text:
                    # 간단한 매칭 로직 (Preferred 문구가 근처에 있으면 성공)
                    status = "preferred" if "Preferred" in text else "non-preferred"
                    return {
                        "adalimumab": {
                            "status": status, 
                            "detail": "Live Data (TX)", 
                            "is_sb": True
                        }
                    }
        
        return {"adalimumab": {"status": "non-preferred", "detail": "Adalimumab not found", "is_sb": False}}

    except Exception as e:
        print(f"[TX Parser] Critical Error: {e}")
        raise e
