# main.py

from fastapi import FastAPI
from api.elaborate import router as elaborate_router
from api.summarize import router as summarize_router

app = FastAPI(title="AI Literature Server (GGUF)")

# --- 1. 미들웨어 및 모니터링 설정 ---
# app.add_middleware(PrometheusMiddleware, app_name="ai_literature_server")
# app.include_router(MetricsManager.router)


app.include_router(elaborate_router, prefix="/api", tags=["Elaborate"])
app.include_router(summarize_router, prefix="/api", tags=["Summarize"])

# 모델 로드 및 헬퍼 함수는 /app/services/llm_inference.py 로 이동했으므로 삭제
# Pydantic 모델 정의도 /app/schemas/literatures.py 로 이동했으므로 삭제