# /app/services/llm_inference.py

from typing import List, Dict, Optional
from core.model_loader import GGUFModel # runner는 프로젝트 루트에 있다고 가정

# 모델 인스턴스는 한 번만 로드
# 주의: model path가 실제 파일 경로와 일치하는지 꼭 확인하세요.
# n_parallel=1, n_batch=512 (max length 기준) 설정은 유지
model = GGUFModel(
    model_path="model/gemma-3-1b-it-q4_0.gguf", 
    max_ctx=2048,
    gpu_layers=20
)


def run_inference(system_prompt: str, user_input: str, max_tokens: int, stop_tokens: Optional[List[str]] = None) -> str:
    """단발성 질문/요청 처리를 위한 공통 LLM 호출 헬퍼"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    # n_parallel=1이므로 max_tokens=256과 n_batch=512로 설정된 model.chat을 사용
    return model.chat(messages, max_tokens=max_tokens )


# --- API에서 호출될 구체적인 서비스 함수 (비즈니스 로직) ---

def elaborate_service(text: str) -> str:
    """문장 구체화 로직"""
    system_prompt = (
        "너는 문학적 표현을 풍부하게 만드는 작가야. "
        "사용자가 입력한 문장의 의미를 유지하되, "
        "더 감성적이고 시적인 문체로 다듬고 확장해서 작성해줘."
    )
    # 짧은 응답(Elaborate)을 위해 max_tokens=128로 설정 (최적화)
    return run_inference(system_prompt, text, max_tokens=256)

def summarize_service(conversation: List[Dict]) -> str:
    """대화 요약 로직"""
    system_prompt = """
너는 감정 코칭 대화를 정리하는 문학적 요약 전문가야.
대화의 흐름 속에서 사용자가 느낀 감정, 변화, 깨달음을 한 편의 짧은 산문처럼 정리해.
형식적으로 1,2,3으로 구분하지 말고, 자연스럽게 하나의 글로 써줘.
""".strip()
    
    messages = [{"role": "system", "content": system_prompt}] + conversation
    
    # 긴 응답(Summarize)을 위해 max_tokens=512로 설정 (최적화)
    # n_batch=512를 통해 긴 입력도 효율적으로 처리
    return model.chat(messages, max_tokens=512, )