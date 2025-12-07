from pydantic import BaseModel
class ElaborateRequest(BaseModel):
    text: str 

class ElaborateResponse(BaseModel):
    elaborated_text: str
