# ---- Base: CUDA + PyTorch ----
FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

# ---- 기본 세팅 ----
ENV DEBIAN_FRONTEND=noninteractive

# 기본 유틸 설치
RUN apt-get update && apt-get install -y \
    python3 python3-pip git wget curl && \
    rm -rf /var/lib/apt/lists/*

# ---- 워킹 디렉토리 ----
WORKDIR /app

# ---- 의존성 복사 및 설치 ----
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# ---- 앱 코드 복사 ----
COPY ./app /app

# ---- FastAPI 실행 ----
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
