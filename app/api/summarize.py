from fastapi import APIRouter
from schemas.conversation import ConversationSummaryRequest, ConversationSummaryResponse
from services.llm_inference import summarize_service # 서비스 로직 import

router = APIRouter()

@router.post("/summarize", response_model=ConversationSummaryResponse)
def summarize_conversation_api(request: ConversationSummaryRequest):
    # Pydantic 모델(ConversationTurn) -> Dict 변환
    conversation_dicts = []
    for t in request.conversation:
        role = t.role.lower()
        if role not in ["user", "assistant"]:
            role = "user"
        conversation_dicts.append({"role": role, "content": t.content})
        
    # 서비스 로직 호출
    summary_text = summarize_service(conversation_dicts)

    return ConversationSummaryResponse(
        summary=summary_text.strip(),
        emotional_flow="감정 흐름 분석 데이터 (예시)",
        insight="통찰 메시지 (예시)"
    )