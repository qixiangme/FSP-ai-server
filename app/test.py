# test_ai_server.py
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_interpret():
    url = f"{BASE_URL}/api/interpret"
    data = {
        "poem": """
가야 할 때가 언제인가를
분명히 알고 가는 이의
뒷모습은 얼마나 아름다운가.

봄 한철
격정을 인내한
나의 사랑은 지고 있다.
"""
    }
    response = requests.post(url, json=data)
    print("\n=== /api/interpret ===")
    print("Status:", response.status_code)
    try:
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
    except Exception:
        print(response.text)

def test_elaborate():
    url = f"{BASE_URL}/api/elaborate"
    data = {
        "text": "분명히 알고 가는 이의 뒷모습은 아름답다.이 구절에서 느낀 슬픔과 애틋함이 느껴져."
    }
    response = requests.post(url, json=data)
    print("\n=== /api/elaborate ===")
    print("Status:", response.status_code)
    try:
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
    except Exception:
        print(response.text)

def test_summarize():
    url = f"{BASE_URL}/api/summarize"
    data = {
        "conversation": [
            {"role": "user", "content": "이 구절에서 느껴지는 감정을 설명해줘."},
            {"role": "assistant", "content": "사용자가 느낀 슬픔과 애틋함이 담겨있어."},
            {"role": "user", "content": "좀 더 구체적으로 문학적으로 풀어줘."}
        ]
    }
    response = requests.post(url, json=data)
    print("\n=== /api/summarize ===")
    print("Status:", response.status_code)
    try:
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
    except Exception:
        print(response.text)

if __name__ == "__main__":
    test_elaborate()
    test_summarize()
