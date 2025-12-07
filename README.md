
## FSP-ai-server 개요

* FastAPI 기반 AI Inference 서버
* Google Gemma 3-4B IT QAT Q4_0 GGUF 모델 사용
* llama.cpp로 모델을 Python 환경에서 직접 로딩
* Docker 기반 배포 지원
* API / Service / Core 구조로 계층 분리
* Python 3.11-slim 환경 기준 최적화된 실행 구조 적용

---

## 주요 특징

### FastAPI 기반 서버

* 비동기 구조(asyncio)와 ThreadPoolExecutor 조합
* 동기 LLM 추론을 비차단 방식으로 처리
* 모든 API 호출에 latency 로깅 적용

### Llama.cpp 모델 서빙

* gemma-3-1b-it-qat-q4_0-gguf 모델 로딩
* Q4_0 양자화 모델로 메모리 사용량 최소화
* gpu_layers=999 설정으로 GPU 가속 최대 적용
* n_batch, n_threads 등 llama.cpp 파라미터 조정 가능
* model_loader 모듈만 수정하면 모델 교체 가능

### 아키텍처 구성

* /api: 라우팅 계층
* /schemas: 요청·응답 스키마 정의
* /services: 프롬프트 구성, 전처리 등 비즈니스 로직
* /llm_core: 모델 로딩, llama.cpp 실행 엔진, 최적화 파라미터 관리
* API → Service → Model(Core)의 계층이 명확하게 분리됨
* Core-Server ↔ AI-Server 간 Facade 추상화 적용

---

## Core-Server 연동 최적화

* summaryText → 모델 입력 변환 파싱 로직을 별도 쓰레드에서 수행
* 입력 전처리 지연 감소
* Spring WebClient 비동기 통신으로 왕복 시간 최소화
* 전체 응답 처리 속도 개선

---

## Docker 기반 실행 환경

### 사용 베이스 이미지

* python:3.11-slim
* 경량 이미지 기반으로 불필요한 패키지 제거

### 시스템 패키지 구성

* git, wget, curl, build-essential 설치
* llama.cpp 빌드 및 Python binding 사용 환경과 호환

### Python 가상환경 구성

* /opt/venv 위치에 venv 생성
* PATH에 venv/bin 등록
* pip 최신 버전으로 업데이트 후 패키지 설치


---

## 요구사항

* Python 3.11
* Docker
* llama.cpp

---

## 설치 및 실행

### 1) 저장소 클론

```
git clone https://github.com/qixiangme/FSP-ai-server.git
cd FSP-ai-server
```

### 2) 환경 변수 설정

* config.py 또는 .env에 모델 경로 등 지정

### 3) Docker 실행 (권장)

```
docker build -t fsp-ai-server .
docker run -p 8000:8000 fsp-ai-server
```

### 4) 로컬 실행

```
pip install -r requirements.txt
python app.py
```

---

필요하면 **문서화 정량·정성 평가 항목(3~9번)**에 맞춰 채점형 버전으로도 재구성해줄까?
