import json
import os
import random

def run_pipeline():
    # 미국 50개 주 리스트
    states = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]
    
    results = {}
    details = ["Exclusive", "1 of 2", "1 of 3"]

    for state in states:
        # 테스트를 위해 랜덤하게 상태 부여
        status_choice = random.choice(["preferred", "non-preferred"])
        if status_choice == "preferred":
            detail_choice = random.choice(details)
            is_sb = True # 삼성 바이오에피스 제품 가정
        else:
            detail_choice = "Non-Preferred"
            is_sb = False
        
        results[state] = {
            "adalimumab": {
                "status": status_choice,
                "detail": detail_choice,
                "is_sb": is_sb
            }
        }
    
    # 데이터 저장 폴더 생성 및 저장
    os.makedirs('data/current', exist_ok=True)
    with open('data/current/aggregated.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"Successfully generated data for {len(states)} states.")

if __name__ == "__main__":
    run_pipeline()
