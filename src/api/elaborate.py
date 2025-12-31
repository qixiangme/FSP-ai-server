from fastapi import APIRouter
from src.schemas.elaborate import ElaborateRequest, ElaborateResponse
from src.services.llm_inference import elaborate_service_async
import time
import psutil
import asyncio

router = APIRouter()

@router.post("/elaborate", response_model=ElaborateResponse)
async def elaborate_text_api(request: ElaborateRequest):
    process = psutil.Process()

    # 요청 전 측정
    mem_before = psutil.virtual_memory().used
    cpu_before = process.cpu_times()
    t0 = time.time()

    # ----------- CPU 폴링 태스크 정의 -----------
    cpu_percent_list = []
    stop_polling = False

    async def poll_cpu(interval=0.1):
        while not stop_polling:
            cpu_percent_list.append(process.cpu_percent(interval=0.0))  # 논블로킹
            await asyncio.sleep(interval)

    polling_task = asyncio.create_task(poll_cpu())

    # ----------- LLM 추론 수행 -----------
    result = await elaborate_service_async(request.text)
    text = result["text"]
    prompt_tokens = result["prompt_tokens"]
    generated_tokens = result["generated_tokens"]
    total_tokens = result["total_tokens"]

    # ----------- CPU 폴링 종료 -----------
    stop_polling = True
    await polling_task

    # 요청 후 측정
    t1 = time.time()
    mem_after = psutil.virtual_memory().used
    cpu_after = process.cpu_times()

    cpu_used_sec = (cpu_after.user + cpu_after.system) - (cpu_before.user + cpu_before.system)
    latency = t1 - t0
    tokens_per_sec = generated_tokens / latency if latency > 0 else 0
    cpu_per_token = cpu_used_sec / generated_tokens if generated_tokens > 0 else 0
    avg_cpu_cores = cpu_used_sec / latency if latency > 0 else 0
    mem_delta_mb = (mem_after - mem_before) // 1024 // 1024
    avg_cpu_percent = sum(cpu_percent_list) / len(cpu_percent_list) if cpu_percent_list else 0
    max_cpu_percent = max(cpu_percent_list) if cpu_percent_list else 0

    # ------------------ 로그 출력 ------------------
    print("===== LLM BENCHMARK =====")
    print(f"LATENCY            : {latency:.3f} s")
    print(f"CPU time used      : {cpu_used_sec:.3f} s")
    print(f"Avg CPU cores used : {avg_cpu_cores:.2f}")
    print(f"Avg CPU %          : {avg_cpu_percent:.1f}%")
    print(f"Max CPU %          : {max_cpu_percent:.1f}%")
    print(f"Memory delta       : {mem_delta_mb} MB")
    print(f"Prompt tokens      : {prompt_tokens}")
    print(f"Generated tokens   : {generated_tokens}")
    print(f"Total tokens       : {total_tokens}")
    print(f"Tokens / second    : {tokens_per_sec:.2f}")
    print(f"CPU sec / token    : {cpu_per_token:.3f}")
    print("==========================")

    return ElaborateResponse(elaborated_text=text.strip())
