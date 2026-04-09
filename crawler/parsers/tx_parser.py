import os
import re
import tempfile
import requests
import pdfplumber

def get_tx_data(pdf_url: str) -> dict:
    """
    텍사스(TX) Medicaid PDL PDF 파일 URL을 받아 Adalimumab 관련 데이터를 파싱합니다.
    """
    print(f"[TX Parser] Downloading PDF from: {pdf_url}")
    response = requests.get(pdf_url, stream=True)
    response.raise_for_status()
    
    # 임시 파일로 PDF 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        for chunk in response.iter_content(chunk_size=8192):
            tmp_file.write(chunk)
        tmp_file_path = tmp_file.name

    # 반환할 초기 데이터 구조
    result = {
        "adalimumab": {
            "status": "no-data",
            "detail": "N/A",
            "is_sb": False
        }
    }

    try:
        print("[TX Parser] Parsing PDF...")
        with pdfplumber.open(tmp_file_path) as pdf:
            found_adalimumab = False
            
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if not text:
                    continue
                
                # 라인 단위로 읽으며 Adalimumab 찾기
                lines = text.split('\n')
                for line in lines:
                    line_lower = line.lower()
                    
                    if 'adalimumab' in line_lower:
                        found_adalimumab = True
                        print(f"[TX Parser] Found 'Adalimumab' on page {page_num}: {line.strip()}")
                        
                        # 1. 상태(status) 분석: 'non-preferred', 'np' 등 키워드로 우선 파악
                        if re.search(r'\b(non-preferred|non preferred|np)\b', line_lower):
                            result["adalimumab"]["status"] = "non-preferred"
                        elif re.search(r'\b(preferred|p)\b', line_lower):
                            result["adalimumab"]["status"] = "preferred"
                            
                        # 2. 상세(detail) 분석: 'exclusive' 등 
                        if 'exclusive' in line_lower:
                            result["adalimumab"]["detail"] = "Exclusive"
                        else:
                            # 필요에 따라 정규식으로 '1 of 2', '1 of 3' 등 추출 로직 추가 가능
                            # 현재는 N/A 혹은 식별불가 시 N/A로 둠
                            pass
                            
                        # 3. 제품 여부(is_sb): 삼성바이오에피스 제품인 하들리마(Hadlima) 포함 여부 등
                        if 'hadlima' in line_lower or 'samsung' in line_lower:
                            result["adalimumab"]["is_sb"] = True
                            
                        # 최초 발견된 행을 기준으로 데이터를 구성하고 종료 (데이터에 따라 수정 필요)
                        break
                        
                if found_adalimumab and result["adalimumab"]["status"] != "no-data":
                    break
                    
    except Exception as e:
        print(f"[TX Parser] Error during PDF parsing: {e}")
    finally:
        # 구문 분석 완료 후 임시 파일 삭제
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

    return result

# 테스트용 로직 (직접 실행 시)
if __name__ == "__main__":
    # 예시: Texas HHS Vendor Drug Program에서 제공하는 가상의(혹은 실제) 최신 PDL PDF URL
    sample_url = "https://www.txvendordrug.com/sites/default/files/docs/pdl/preferred-drug-list.pdf"
    
    print("Testing TX Parser with Sample URL...")
    try:
        data = get_tx_data(sample_url)
        print("\n[Result Data]")
        print(data)
    except Exception as err:
        print(f"Test failed. Make sure the URL is valid. Error: {err}")
