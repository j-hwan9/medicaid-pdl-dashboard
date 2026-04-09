import json
import os
import random
from datetime import datetime, timezone

def run_pipeline():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    manual_path = os.path.join(current_dir, 'manual_data.json')

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
        # (A) 크롤러 완성된 주
        if state == "TX":
            try:
                from parsers.tx_parser import get_tx_data
                tx_results = get_tx_data()
                # tx_parser가 이제 {drug: {...}} dict 반환
                results[state] = tx_results
            except Exception as e:
                print(f"TX 크롤링 실패: {e}")
                if "TX" in manual_data:
                    results[state] = manual_data["TX"]
                else:
                    results[state] = {
                        "adalimumab": {"status": "error", "detail": str(e), "is_sb": False},
                        "ustekinumab": {"status": "error", "detail": str(e), "is_sb": False},
                    }

        # (B) 수동 입력 주
        elif state in manual_data:
            results[state] = manual_data[state]

        # (C) 샘플 데이터
        else:
            results[state] = {
                "adalimumab": {
                    "status": random.choice(["preferred", "non-preferred"]),
                    "detail": "Sample Data",
                    "is_sb": False,
                    "pa_required": None,
                },
                "ustekinumab": {
                    "status": random.choice(["preferred", "non-preferred"]),
                    "detail": "Sample Data",
                    "is_sb": False,
                    "pa_required": None,
                }
            }

    # 메타데이터 포함 저장
    output = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "states": results
    }

    output_dir = os.path.join(current_dir, '..', 'data', 'current')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'aggregated.json')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"[Pipeline] Done. Output: {output_path}")

if __name__ == "__main__":
    run_pipeline()
