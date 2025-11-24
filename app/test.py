# test_ai_server.py
import requests
import json
from typing import Any, Dict, Optional

BASE_URL = "http://127.0.0.1:8000"


# -----------------------------
# 공통 요청 함수
# -----------------------------
def send_post(endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.post(url, json=payload, timeout=30)
    except Exception as e:
        print(f"[ERROR] 요청 실패: {endpoint} -> {e}")
        return None

    print(f"\n=== {endpoint} ===")
    print("Status:", response.status_code)

    try:
        data = response.json()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return data
    except Exception:
        print("[WARN] JSON 디코딩 실패 — 원본 응답:")
        print(response.text)
        return None


def test_elaborate():
    payload = {
        "text": "분명히 알고 가는 이의 뒷모습은 아름답다. 이 구절에서 느낀 슬픔과 애틋함이 느껴져."
    }
    return send_post("/api/elaborate", payload)


def test_summarize():
    payload = {
        "conversation": [
            {"role": "user", "content": "이 구절에서 느껴지는 감정을 설명해줘."},
            {"role": "assistant", "content": "사용자가 느낀 슬픔과 애틋함이 담겨있어."},
            {"role": "user", "content": "좀 더 구체적으로 문학적으로 풀어줘."}
        ]
    }
    return send_post("/api/summarize", payload)


# -----------------------------
# 실행 메인
# -----------------------------
if __name__ == "__main__":
    print("=== AI 서버 테스트 시작 ===")

    # 필요한 것만 골라 테스트 가능
    test_elaborate()
    test_summarize()
    # test_interpret()  # 필요하면 주석 해제

    print("\n=== 테스트 종료 ===")
