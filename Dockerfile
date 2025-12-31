FROM python:3.11-slim

# apt 설치 시 사용자 입력 방지
ENV DEBIAN_FRONTEND=noninteractive

# 로케일 설정
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Python 로그 즉시 출력
ENV PYTHONUNBUFFERED=1

# Python 가상환경 경로
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# src import 안정화를 위한 PYTHONPATH
ENV PYTHONPATH=/app

# 필수 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# 가상환경 생성 및 pip 업그레이드
RUN python -m venv $VIRTUAL_ENV && \
    pip install --upgrade pip

# 작업 디렉터리
WORKDIR /app

# requirements 먼저 복사 (캐시 최적화)
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# 소스 코드만 복사 (model 제외)
COPY src ./src

# FastAPI 포트
EXPOSE 8000

# 서버 실행
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
