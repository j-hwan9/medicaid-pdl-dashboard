import json
import os

def run_pipeline():
    # 실제 구현 시 각 주(State)별 크롤러 클래스 호출 [cite: 557, 590]
    print("Starting US Medicaid PDL Crawl...")
    
    # 예시 데이터 생성 (실제 크롤링 로직이 들어갈 자리)
    mock_data = {
        "TX": {"adalimumab": {"status": "preferred", "sb_product": True}},
        "FL": {"adalimumab": {"status": "non-preferred", "sb_product": False}}
    }
    
    os.makedirs('data/current', exist_ok=True)
    with open('data/current/aggregated.json', 'w') as f:
        json.dump(mock_data, f, indent=2)
    print("Data saved to data/current/aggregated.json")

if __name__ == "__main__":
    run_pipeline()