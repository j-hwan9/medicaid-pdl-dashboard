import json
import os
import random

def run_pipeline():
    # 1. 설정 파일 읽기
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # 전체 50개 주 리스트 (기본 리스트)
    all_states = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]
    
    results = {}

    for state in all_states:
        # 2. config에 등록된 주(진짜 크롤링 대상)인지 확인
        if state in config['states']:
            # 지금은 TX 파서만 연결 (NY 등은 추후 확장)
            if state == "TX":
                try:
                    from parsers.tx_parser import get_tx_data
                    results[state] = get_tx_data()
                except Exception as e:
                    print(f"{state} 크롤링 실패: {e}")
                    results[state] = {"adalimumab": {"status": "error", "detail": "Parsing Failed", "is_sb": False}}
            else:
                # 등록은 됐지만 파서가 아직 없는 경우 샘플 데이터
                results[state] = {"adalimumab": {"status": "preferred", "detail": "Pending Parser", "is_sb": False}}
        else:
            # 3. 그 외 주들은 랜덤 샘플 데이터 (화면 유지용)
            status = random.choice(["preferred", "non-preferred"])
            results[state] = {
                "adalimumab": {
                    "status": status,
                    "detail": "Random Sample",
                    "is_sb": False
                }
            }
    
    # 4. JSON 저장 (에러 방지를 위해 ensure_ascii=False 추가)
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'current')
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, 'aggregated.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run_pipeline()
