# schemas/conversation.py
from pydantic import BaseModel, Field
from typing import List, Optional

class ConversationTurn(BaseModel):
    role: str   
    content: str
    sessionId: Optional[str] = None  
    
    class Config:
        extra = "ignore"  

class ConversationSummaryRequest(BaseModel):
    conversation: List[ConversationTurn]
    userId: Optional[int] = None  
    
    class Config:
        extra = "ignore"  

class ConversationSummaryResponse(BaseModel):
    summary: str

