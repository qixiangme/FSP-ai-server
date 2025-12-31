from fastapi import APIRouter, HTTPException, Request
from src.schemas.conversation import ConversationSummaryRequest, ConversationSummaryResponse
from src.services.llm_inference import summarize_service, summarize_service_async
import time
import psutil
import json
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor

router = APIRouter()
executor = ThreadPoolExecutor(max_workers=4)

# ---------------- 문자열 대화 파싱 ----------------
def parse_conversation_string(conv_str: str) -> list:
    """
    문자열로 된 대화를 파싱
    형식: "[USER] message\n[ASSISTANT] response\n..."
    """
    conversations = []
    pattern = r'\[(USER|ASSISTANT)\]\s*(.*?)(?=\n\[(?:USER|ASSISTANT)\]|$)'
    matches = re.finditer(pattern, conv_str, re.DOTALL)

    for match in matches:
        role = match.group(1).lower()
        content = match.group(2).strip()
        if content:
            conversations.append({"role": role, "content": content})

    return conversations

async def parse_in_thread(conv_str: str) -> list:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, parse_conversation_string, conv_str)

# ---------------- summarize API ----------------
@router.post("/summarize", response_model=ConversationSummaryResponse)
async def summarize_conversation_api(raw_request: Request):
    raw_body = await raw_request.body()
    print(f"DEBUG: Raw request body: {raw_body.decode('utf-8')[:200]}...")

    try:
        body_json = json.loads(raw_body)
        print(f"DEBUG: Parsed JSON keys: {body_json.keys()}")

        if isinstance(body_json.get('conversation'), str):
            print("DEBUG: conversation is string, parsing in thread...")
            conv_str = body_json['conversation']
            parsed_conversations = await parse_in_thread(conv_str)
            print(f"DEBUG: Parsed {len(parsed_conversations)} conversation turns")
            if not parsed_conversations:
                raise HTTPException(status_code=400, detail="대화 내역을 파싱할 수 없습니다.")
            conversation_dicts = parsed_conversations

        elif isinstance(body_json.get('conversation'), list):
            print("DEBUG: conversation is list, processing...")
            request_data = ConversationSummaryRequest(**body_json)
            conversation_dicts = [
                {"role": t.role.lower() if t.role.lower() in ["user", "assistant"] else "user",
                 "content": t.content}
                for t in request_data.conversation
            ]
        else:
            raise HTTPException(
                status_code=422, 
                detail=f"conversation 필드가 잘못된 타입입니다: {type(body_json.get('conversation'))}"
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Request parsing error: {e}")
        raise HTTPException(status_code=422, detail=f"요청 형식 오류: {str(e)}")

    # ---------------- CPU 폴링 태스크 정의 ----------------
    process = psutil.Process()
    cpu_percent_list = []
    stop_polling = False

    async def poll_cpu(interval=0.1):
        while not stop_polling:
            cpu_percent_list.append(process.cpu_percent(interval=None))
            await asyncio.sleep(interval)

    polling_task = asyncio.create_task(poll_cpu())

    # ---------------- summarize 수행 ----------------
    mem_before = psutil.virtual_memory().used
    cpu_before = process.cpu_times()
    t0 = time.time()

    try:
        summary_result = await summarize_service_async(conversation_dicts)
    finally:
        stop_polling = True
        await polling_task

    t1 = time.time()
    mem_after = psutil.virtual_memory().used
    cpu_after = process.cpu_times()

    # ---------------- 성능 계산 ----------------
    summary_text = summary_result["text"]
    prompt_tokens = summary_result["prompt_tokens"]
    generated_tokens = summary_result["generated_tokens"]
    total_tokens = summary_result["total_tokens"]
    latency = t1 - t0
    cpu_time_used = (cpu_after.user + cpu_after.system) - (cpu_before.user + cpu_before.system)
    tokens_per_sec = generated_tokens / latency if latency > 0 else 0
    cpu_per_token = cpu_time_used / generated_tokens if generated_tokens > 0 else 0
    mem_delta_mb = (mem_after - mem_before) / 1024 / 1024
    avg_cpu_cores = cpu_time_used / latency if latency > 0 else 0
    avg_cpu_percent = sum(cpu_percent_list) / len(cpu_percent_list) if cpu_percent_list else 0
    max_cpu_percent = max(cpu_percent_list) if cpu_percent_list else 0

    # ---------------- 로그 출력 ----------------
    print("===== SUMMARIZE BENCHMARK =====")
    print(f"LATENCY            : {latency:.3f} s")
    print(f"CPU time used      : {cpu_time_used:.3f} s")
    print(f"Avg CPU cores used : {avg_cpu_cores:.2f}")
    print(f"Avg CPU %          : {avg_cpu_percent:.1f}%")
    print(f"Max CPU %          : {max_cpu_percent:.1f}%")
    print(f"Memory delta       : {mem_delta_mb:.2f} MB")
    print(f"Prompt tokens      : {prompt_tokens}")
    print(f"Generated tokens   : {generated_tokens}")
    print(f"Total tokens       : {total_tokens}")
    print(f"Tokens / second    : {tokens_per_sec:.2f}")
    print(f"CPU sec / token    : {cpu_per_token:.3f}")
    print(f"SUMMARY (100 chars): {summary_text[:100]}...")
    print("===============================")

    return ConversationSummaryResponse(summary=summary_text.strip())
