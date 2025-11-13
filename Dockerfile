# # ---- Base: CUDA + PyTorch ----
# FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04
# # ---- 환경 변수 ----
# ENV DEBIAN_FRONTEND=noninteractive
# ENV LANG=C.UTF-8
# ENV LC_ALL=C.UTF-8
# ENV PYTHONUNBUFFERED=1

# # ---- 필수 패키지 설치 ----
# RUN apt-get update && \
#     apt-get install -y python3 python3-venv python3-pip \
#     git wget curl build-essential cmake libopenblas-dev && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*

# # ---- 작업 디렉토리 ----
# WORKDIR /app

# # ---- venv 생성 ----
# RUN python3 -m venv /opt/venv
# ENV PATH="/opt/venv/bin:$PATH"

# # ---- pip 업그레이드 및 의존성 설치 ----
# COPY requirements.txt /app/
# RUN pip install --upgrade pip
# RUN pip install --no-cache-dir -r requirements.txt

# # ---- 앱 코드 복사 ----
# COPY ./app /app

# # ---- 포트 노출 ----
# EXPOSE 8000

# # ---- FastAPI 실행 ----
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
# ---- Base: CUDA + PyTorch ----
FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04

# ---- 환경 변수 ----
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# ---- 시스템 패키지 설치 ----
# build-essential, cmake 등은 꼭 필요한 경우에만 남기세요.
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-venv python3-pip git wget curl libopenblas-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ---- 작업 디렉토리 ----
WORKDIR /app

# ---- Python venv 생성 및 의존성 설치 ----
# 이 단계는 캐시 활용을 위해 requirements.txt만 먼저 복사합니다.
COPY requirements.txt .
RUN python3 -m venv $VIRTUAL_ENV \
 && pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ---- 앱 코드 복사 ----
COPY ./app .

# ---- 포트 노출 ----
EXPOSE 8000

# ---- 실행 ----
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
