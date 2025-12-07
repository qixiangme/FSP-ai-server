from fastapi import APIRouter
from schemas.elaborate import ElaborateRequest, ElaborateResponse
from services.llm_inference import elaborate_service ,elaborate_service_async# 서비스 로직 import
import time
router = APIRouter()

@router.post("/elaborate", response_model=ElaborateResponse)
async def elaborate_text_api(request: ElaborateRequest):
    start = time.time()
    result_text = await elaborate_service_async(request.text)
    duration = time.time() - start
    print(f"LATENCY : {duration}")
    return ElaborateResponse(elaborated_text=result_text.strip())

