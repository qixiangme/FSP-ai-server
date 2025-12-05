from fastapi import APIRouter
from schemas.elaborate import ElaborateRequest, ElaborateResponse
from services.llm_inference import elaborate_service # 서비스 로직 import
import time
router = APIRouter()

@router.post("/elaborate", response_model=ElaborateResponse)
def elaborate_text_api(request: ElaborateRequest):
    # 서비스 로직 호출
    start = time.time()
    result_text = elaborate_service(request.text)
    duration = time.time() - start
    print(f"LATENCY : {duration}")
    return ElaborateResponse(elaborated_text=result_text.strip())

