from pydantic import BaseModel
class ElaborateRequest(BaseModel):
    text: str  # test_elaborate의 payload {"text": "..."} 와 일치

class ElaborateResponse(BaseModel):
    elaborated_text: str
