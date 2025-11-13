# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from vllm import LLM, SamplingParams

app = FastAPI(title="AI Literature Server (vLLM)")

# ===== 데이터 모델 =====
class PoemRequest(BaseModel):
    poem: str

class ElaborationRequest(BaseModel):
    text: str  # 시 전체 + 선택 구절 + 느낀점 등을 한 문자열로 받음

class ConversationTurn(BaseModel):
    role: str   # "user" or "assistant"
    content: str

class ConversationSummaryRequest(BaseModel):
    conversation: List[ConversationTurn]

class ConversationSummaryResponse(BaseModel):
    summary: str

# ===== 모델 로드 =====
MODEL_NAME = "Qwen/Qwen3-0.6B"
llm = LLM(
    model=MODEL_NAME,
    tensor_parallel_size=1,
    gpu_memory_utilization=0.7,
    max_model_len=2048  # 기존 40960 → 2048로 축소
)


# ===== Helper 함수 =====
def generate_text(messages: List[dict], max_new_tokens: int = 256) -> str:
    """
    vLLM 기반 추론 함수
    """
    # messages를 단일 문자열로 합치기
    prompt = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in messages])

    # 샘플링 설정
    sampling_params = SamplingParams(
        temperature=0.7,
        top_p=0.9,
        max_output_tokens=max_new_tokens
    )

    # 추론
    response = llm.generate(prompt, sampling_params=sampling_params)

    # 첫 번째 응답 텍스트 반환
    return response[0].outputs[0].text.strip()

# ===== 2. 구절/감정 구체화 API =====
@app.post("/api/elaborate")
def elaborate(request: ElaborationRequest):
    system_prompt = """
너는 시의 감정에 공감하며 표현을 확장하는 문학 감정 코치야.
사용자는 시 한 편과 그 중 인상 깊은 구절을 함께 제시한다.
너는 그 구절이 품은 감정을 공감하고, 시 전체 맥락 속에서 그 감정을
더 구체적이고 문학적으로 풀어내야 한다.

단, 해석을 길게 늘어놓지 말고 감정의 결을 ‘짙게’ 느끼는 듯한 표현으로 써라.
사용자에게 ‘위로받는 느낌’을 줄 수 있도록 따뜻하게 공감하며 말해줘.

그리고 무조건 한국어로 말해줘

[예시1]
입력:
시:
바람은 말없이 창가를 스친다  
그대 이름을 부르지 못한 채  
밤하늘만 바라본다

선택 구절: "그대 이름을 부르지 못한 채" 
느낀점: 슬프다

---

출력:
그 이름을 삼킨 마음 속엔 수많은 말들이 갇혀 있죠.  
부르지 못한 이름은 결국 그리움의 그림자가 되어,  
밤하늘에 흩어진 별빛처럼 조용히 당신 곁을 맴돌고 있어요.

[예시2]
입력:
---
시:
낡은 신발 끈을 고쳐 묶으며  
내일의 길을 떠올린다  
조금은 두렵지만, 걸어야 한다

선택 구절: "조금은 두렵지만, 걸어야 한다" 
느낀점: 공감된다

출력:
그 두려움 속에서도 당신은 멈추지 않네요.  
낡은 끈을 다시 묶는 그 손끝엔 포기하지 않으려는 용기가 숨어 있어요.  
그 한 걸음이 이미 내일을 향한 첫 희망이에요.
    """.strip()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request.text}
    ]
    content = generate_text(messages)
    return {"elaboration": content}

# ===== 3. 대화 요약 API =====
@app.post("/api/summarize", response_model=ConversationSummaryResponse)
def summarize_conversation(request: ConversationSummaryRequest):
    dialogue_text = "\n".join([f"{t.role.upper()}: {t.content}" for t in request.conversation])

    system_prompt = """
너는 감정 코칭 대화를 정리하는 문학적 요약 전문가야.
대화의 흐름 속에서 사용자가 느낀 감정, 변화, 깨달음을 한 편의 짧은 산문처럼 정리해.
형식적으로 1,2,3으로 구분하지 말고, 다음 세 가지가 자연스럽게 녹아들게 써.

- 전체적인 대화 요약 (무슨 이야기를 나눴는가)
- 감정 구체화 (사용자의 감정이 어떤 결로 움직였는가)
- 느낀 점 또는 통찰 (마지막에 남은 울림이나 여운)

언어는 부드럽고 시적인 톤을 유지하되, 너무 꾸미지 말고 진솔하게 표현해.
그리고 무조건 한국어로 말해줘
아래는 참고 예시야.

[예시1]
대화는 잊힌 기억 속에서 다시 마주한 외로움에 대한 이야기였다.  
처음엔 스스로의 감정을 설명하기 어려워했지만, 점차 그 감정이 ‘그리움’임을 깨닫는다.  
대화의 끝에는 혼자임에도 괜찮다는, 묘한 평온이 찾아왔다.

[예시2]
사용자는 자신을 몰아세우던 불안을 털어놓았다.  
이야기를 이어가며 그 불안이 ‘멈추고 싶다는 신호’였음을 이해하게 된다.  
결국, 마음을 잠시 쉬게 하는 것이 용기라는 걸 배웠다.

이제 아래 대화를 읽고, 같은 방식으로 정리해줘.
    """.strip()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"--- 대화 로그 ---\n{dialogue_text}"}
    ]

    output_text = generate_text(messages, max_new_tokens=512)
    return ConversationSummaryResponse(summary=output_text.strip())
