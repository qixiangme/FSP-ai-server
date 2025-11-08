# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = FastAPI(title="AI Literature Server")

# ===== 데이터 모델 =====
class PoemRequest(BaseModel):
    poem: str

class ElaborationRequest(BaseModel):
    text: str  # 선택 구절 + 사용자 감정을 합친 하나의 문자열

class ConversationTurn(BaseModel):
    role: str   # "user" or "assistant"
    content: str

class ConversationSummaryRequest(BaseModel):
    conversation: List[ConversationTurn]

class ConversationSummaryResponse(BaseModel):
    summary: str
    emotional_flow: str
    insight: str

# ===== 모델 로드 =====
MODEL_NAME = "Qwen/Qwen3-0.6B"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto"
)

# ===== Helper 함수 =====
def generate_text(messages: List[dict], max_new_tokens=256) -> str:
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True
    )
    inputs = tokenizer([text], return_tensors="pt").to(model.device)
    generated_ids = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        temperature=0.7,
        top_p=0.9,
        do_sample=True
    )
    output_ids = generated_ids[0][len(inputs.input_ids[0]):].tolist()
    try:
        index = len(output_ids) - output_ids[::-1].index(151668)  # </think> 토큰
    except ValueError:
        index = 0
    thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip()
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip()
    return content, thinking_content

# ===== 1. 시 분석 API =====
@app.post("/api/interpret")
def interpret(request: PoemRequest):
    messages = [
        {"role": "system", "content": "너는 섬세한 문학 평론가야."},
        {"role": "user", "content": f"다음 시를 분석해서 주제, 감정, 상징을 3줄로 간결하게 설명해줘:\n---\n{request.poem}"}
    ]
    content, thinking = generate_text(messages)
    return {"interpretation": content, "thinking": thinking}

# ===== 2. 구절/감정 구체화 API =====
@app.post("/api/elaborate")
def elaborate(request: ElaborationRequest):
    messages = [
        {"role": "system", "content": "너는 섬세한 문학 평론가야."},
        {"role": "user", "content": f"{request.text}\n이 감정을 더 구체적이고 문학적으로 확장해서 설명해줘."}
    ]
    content, thinking = generate_text(messages)
    return {"elaboration": content, "thinking": thinking}

# ===== 3. 대화 요약 API =====
@app.post("/api/summarize", response_model=ConversationSummaryResponse)
def summarize_conversation(request: ConversationSummaryRequest):
    dialogue_text = "\n".join([f"{t.role.upper()}: {t.content}" for t in request.conversation])
    prompt = f"""
너는 문학 감정 코치의 대화 기록을 요약하는 AI야.
다음은 사용자와 너의 감정 대화 로그야. 이를 기반으로 세 가지를 생성해줘:

1. 대화의 전체 요약 (사용자가 느낀 감정과 주제 흐름)
2. 감정의 변화나 흐름 설명 (초기 → 중간 → 마지막)
3. 대화에서 드러난 통찰 또는 핵심 구절 (1~2문장)

--- 대화 ---
{dialogue_text}
"""
    messages = [
        {"role": "system", "content": "너는 감정 분석과 문학 요약 전문가야."},
        {"role": "user", "content": prompt}
    ]
    output_text, _ = generate_text(messages, max_new_tokens=512)
    parts = output_text.split("\n")
    summary = parts[0] if len(parts) > 0 else ""
    emotional_flow = parts[1] if len(parts) > 1 else ""
    insight = parts[2] if len(parts) > 2 else ""
    return ConversationSummaryResponse(summary=summary.strip(), emotional_flow=emotional_flow.strip(), insight=insight.strip())
