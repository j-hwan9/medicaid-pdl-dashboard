import json
import os

def run_pipeline():
    # 실제 구현 시 각 주(State)별 크롤러 클래스 호출 [cite: 557, 590]
    print("Starting US Medicaid PDL Crawl...")
    
    # 50개 주 이름 (기획안 Appendix 참고)
    states = [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", 
        "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", 
        "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", 
        "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", 
        "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", 
        "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", 
        "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", 
        "Wisconsin", "Wyoming"
    ]

    import random
    
    mock_data = {}
    for state in states:
        status_choice = random.choice(["preferred", "non-preferred", "no-data"])
        if status_choice == "preferred":
            detail = random.choice(["Exclusive", "1 of 2", "1 of 3"])
            is_sb = random.choice([True, False])
            mock_data[state] = {
                "adalimumab": {
                    "status": "preferred",
                    "detail": detail,
                    "is_sb": is_sb
                }
            }
        elif status_choice == "non-preferred":
            mock_data[state] = {
                "adalimumab": {
                    "status": "non-preferred",
                    "detail": "N/A",
                    "is_sb": False
                }
            }
        # no-data의 경우 빈 객체이거나 항목을 넣지 않을 수 있음. 여기서는 상태값을 생략
            
    os.makedirs('data/current', exist_ok=True)
    with open('data/current/aggregated.json', 'w') as f:
        json.dump(mock_data, f, indent=2)
    print("Data saved to data/current/aggregated.json")

if __name__ == "__main__":
    run_pipeline()
