# ---- Base: CUDA 12.6 + Ubuntu 22.04 ----
FROM nvidia/cuda:12.6.0-devel-ubuntu22.04

# ---- Environment ----
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# ---- System dependencies ----
RUN apt-get update && apt-get install -y \
    python3 python3-pip git wget curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# ---- uv 설치 ----
RUN pip install --upgrade pip && pip install uv

# ---- 작업 디렉토리 ----
WORKDIR /app

# ---- Python 패키지 설치 (requirements만 이미지에 포함) ----
COPY requirements.txt /tmp/requirements.txt
RUN uv pip install --system -r /tmp/requirements.txt

# ---- 코드/모델은 외부에서 마운트 ----
# /app 내부는 비워둠

EXPOSE 8000

# ---- FastAPI 실행 ----
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
