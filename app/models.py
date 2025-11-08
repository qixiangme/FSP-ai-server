from pydantic import BaseModel

class PoemRequest(BaseModel):
    poem: str

class PoemResponse(BaseModel):
    interpretation: str