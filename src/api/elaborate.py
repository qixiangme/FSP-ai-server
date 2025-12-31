from fastapi import APIRouter
from src.schemas.elaborate import ElaborateRequest, ElaborateResponse
from src.services.llm_inference import elaborate_service ,elaborate_service_async# 서비스 로직 import
import time
import psutil
router = APIRouter()

@router.post("/elaborate", response_model=ElaborateResponse)
async def elaborate_text_api(request: ElaborateRequest):
    vm = psutil.virtual_memory()
    start = time.time()
    result_text = await elaborate_service_async(request.text)
    duration = time.time() - start
    print(f"LATENCY : {duration}")
    print(f"CPU_percent : {psutil.cpu_percent(interval=0.1)}")
    print(f"memory_used_mb : {vm.used // 1024 // 1024}")
    print(f"memory_total_mb : {vm.total // 1024 // 1024}")

    return ElaborateResponse(elaborated_text=result_text.strip())

