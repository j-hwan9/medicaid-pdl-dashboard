import json
import os
import random
# 1. 방금 만든 TX 파서를 불러옵니다
from parsers.tx_parser import get_tx_data 

def run_pipeline():
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", ...] # 50개 주 리스트
    results = {}

    for state in states:
        if state == "TX":
            # 2. Texas는 진짜 데이터를 가져옵니다
            try:
                results["TX"] = get_tx_data()
            except Exception as e:
                print(f"TX 파싱 에러: {e}")
                # 에러 날 경우를 대비한 기본값
                results["TX"] = {"adalimumab": {"status": "non-preferred", "detail": "Error", "is_sb": False}}
        else:
            # 3. 나머지는 아직 랜덤 데이터 유지
            status_choice = random.choice(["preferred", "non-preferred"])
            results[state] = {
                "adalimumab": {
                    "status": status_choice,
                    "detail": "Random Sample",
                    "is_sb": False
                }
            }
    
    # 데이터 저장
    os.makedirs('data/current', exist_ok=True)
    with open('data/current/aggregated.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_pipeline()
