from fastapi import APIRouter, HTTPException, Request
from schemas.conversation import ConversationSummaryRequest, ConversationSummaryResponse
from services.llm_inference import summarize_service,summarize_service_async
import time
import json
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor

router = APIRouter()
executor = ThreadPoolExecutor(max_workers=4)

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
            
            # 쓰레드에서 파싱
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
    
    try:
        print(f"DEBUG: Processing {len(conversation_dicts)} conversation turns")
        start = time.time()
        summary_text = await summarize_service_async(conversation_dicts)
        duration = time.time() - start
        
        print(f"LATENCY: {duration:.2f}s")
        print(f"SUMMARY: {summary_text[:100]}...")
        
        return ConversationSummaryResponse(
            summary=summary_text.strip(),
        )
    
    except Exception as e:
        print(f"ERROR in summarize_conversation_api: {str(e)}")
        raise HTTPException(status_code=500, detail=f"요약 생성 중 오류 발생: {str(e)}")
