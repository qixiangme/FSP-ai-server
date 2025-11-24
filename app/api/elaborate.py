from fastapi import APIRouter
from schemas.elaborate import ElaborateRequest, ElaborateResponse
from services.llm_inference import elaborate_service # 서비스 로직 import

router = APIRouter()

@router.post("/elaborate", response_model=ElaborateResponse)
def elaborate_text_api(request: ElaborateRequest):
    # 서비스 로직 호출
    result_text = elaborate_service(request.text)
    
    return ElaborateResponse(elaborated_text=result_text.strip())