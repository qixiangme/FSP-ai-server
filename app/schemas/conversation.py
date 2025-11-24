from pydantic import BaseModel
from typing import List
class ConversationTurn(BaseModel):
    role: str   # "user" or "assistant"
    content: str

class ConversationSummaryRequest(BaseModel):
    conversation: List[ConversationTurn]

class ConversationSummaryResponse(BaseModel):
    summary: str
    emotional_flow: str = "" # 기본값 처리
    insight: str = ""