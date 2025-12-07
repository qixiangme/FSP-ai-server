# main.py

from fastapi import FastAPI
from api.elaborate import router as elaborate_router
from api.summarize import router as summarize_router

app = FastAPI(title="AI Literature Server (GGUF)")



app.include_router(elaborate_router, prefix="/api", tags=["Elaborate"])
app.include_router(summarize_router, prefix="/api", tags=["Summarize"])

