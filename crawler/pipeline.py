import json
import os
import random

def run_pipeline():
    # 1. 파일 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    manual_path = os.path.join(current_dir, 'manual_data.json')
    
    # 2. 수동 입력 데이터 읽기 (있으면 가져오고 없으면 빈 칸)
    manual_data = {}
    if os.path.exists(manual_path):
        with open(manual_path, 'r', encoding='utf-8') as f:
            manual_data = json.load(f)

    all_states = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]
    
    results = {}
    for state in all_states:
        # (A) 진짜 크롤러가 완성된 주 (현재 TX)
        if state == "TX":
            try:
                from parsers.tx_parser import get_tx_data
                pdl_url = "https://www.txvendordrug.com/formulary/prior-authorization/preferred-drugs"
                results[state] = {"adalimumab": get_tx_data(pdl_url)}
            except Exception as e:
                print(f"TX 크롤링 실패, 수동/샘플 데이터로 대체: {e}")
                # 크롤링 실패 시 수동 데이터가 있으면 쓰고, 없으면 에러 표시
                if "TX" in manual_data:
                    results[state] = {"adalimumab": manual_data["TX"]}
                else:
                    results[state] = {"adalimumab": {"status": "error", "detail": "Crawler Error", "is_sb": False}}
        
        # (B) 크롤러는 없지만 내가 직접 확인해서 적어둔 주
        elif state in manual_data:
            results[state] = {"adalimumab": manual_data[state]}
        
        # (C) 아직 아무것도 없는 주 (발표용 랜덤 샘플)
        else:
            status = random.choice(["preferred", "non-preferred"])
            results[state] = {
                "adalimumab": {
                    "status": status,
                    "detail": "Sample Data",
                    "is_sb": False
                }
            }
    
    # 최종 결과 저장
    output_dir = os.path.join(current_dir, '..', 'data', 'current')
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, 'aggregated.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run_pipeline()
