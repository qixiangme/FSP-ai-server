import asyncio
from typing import List, Dict
from src.core.model_loader import GGUFModel

# 모델 로드 (기존 그대로)
model = GGUFModel(
    model_path="/model/Qwen3-0.6B-Q8_0.gguf",
    max_ctx=4096,
    gpu_layers=999,
)

# 동기 inference
def run_inference(system_prompt: str, user_input: str, max_tokens: int):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    return model.chat(messages, max_tokens=max_tokens)


def elaborate_service(text: str) -> str:
    system_prompt = (
        "사용자가 입력한 문장의 의미를 유지하고 공감해줘서 "
        "더 해석을 확장가능하게 해줘 "
        "2~3문장 정도"
    )
    return run_inference(system_prompt, text, max_tokens=128)


def summarize_service(conversation: List[Dict]) -> str:
    system_prompt = """
너는 시(poem)에 대한 감상 대화를 정리하는 문학적 요약 전문가야.
사용자와 AI의 대화 흐름 속에서:
1) 사용자가 시를 통해 느낀 감정과 생각
2) 대화를 통해 발견한 시의 의미와 해석
3) 사용자가 얻은 깨달음이나 감상의 변화

이 세 가지를 자연스럽게 한 편의 짧은 산문으로 정리해줘.
형식적으로 1,2,3으로 구분하지 말고, 마치 감상문처럼 자연스럽게 써줘.
200-300자 내외로 작성해.
""".strip()

    messages = [{"role": "system", "content": system_prompt}] + conversation
    return model.chat(messages, max_tokens=512)


# --------------------
# 비동기 wrapper (FastAPI에서 쓰레드로 안전하게 호출)
# --------------------
async def elaborate_service_async(text: str) -> dict:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, elaborate_service, text)


async def summarize_service_async(conversation: List[Dict]) -> dict:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, summarize_service, conversation)
