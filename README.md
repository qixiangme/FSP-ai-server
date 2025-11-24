# FSP-ai-server

FSP-ai-server는 FastAPI와 Docker, 그리고 Hugging Face의 Google Gemma 3-1B 모델(gemma-3-1b-it-qat-q4_0-gguf)을 활용하는 AI 모델 서빙 서버입니다.
Python(89.9%)와 Dockerfile(10.1%)로 개발되어, 누구나 손쉽게 AI inference API를 사용할 수 있도록 설계되었습니다.

## 주요 특징

- **FastAPI 기반**: 빠르고 견고한 Python 웹 프레임워크인 FastAPI 사용
- **Hugging Face 모델 지원**: [Google Gemma 3-1B QAT Q4_0 모델](https://huggingface.co/google/gemma-3-1b-it-qat-q4_0-gguf) 활용
- **AI Inference 서빙**: AI 모델 서빙 및 추론 API 제공
- **Docker 지원**: 도커 환경에서 손쉬운 배포 및 실행
- **확장성**: 다양한 추가 AI 모델 및 기능 확장에 용이

## 요구사항

- Python 3.8 이상
- Docker
- llama.cpp

## 설치 및 실행 방법

### 1. 저장소 클론

```bash
git clone https://github.com/qixiangme/FSP-ai-server.git
cd FSP-ai-server
```

### 2. 환경 변수/설정

- 필요 시 `config.py` 또는 `.env` 파일에 모델 경로 및 Hugging Face 관련 설정 필요

### 3. Docker로 실행 (권장)

```bash
docker build -t fsp-ai-server .
docker run -p 8000:8000 fsp-ai-server
```

### 4. 로컬에서 바로 실행 (옵션)

```bash
pip install -r requirements.txt
python app.py
```


## 프로젝트 구조
제시된 `/app` 폴더 구조의 핵심은 **FastAPI의 3계층 아키텍처**와 **ML Ops의 핵심 모듈**을 명확히 분리한 것입니다.

| 폴더 | 계층 (역할) | 핵심 기능 |
| :--- | :--- | :--- |
| **`/api/`** | **🌐 라우팅 계층** (인터페이스) | URL을 정의하고 클라이언트 요청/응답을 처리합니다. |
| **`/schemas/`** | **📜 데이터 계층** (정의) | Pydantic을 사용해 **요청 및 응답 데이터 구조**를 정의합니다. |
| **`/services/`** | **🧠 서비스 계층** (비즈니스 로직) | **프롬프트 구성, 전처리** 등 핵심 비즈니스 로직을 수행합니다. |
| **`/llm_core/`** | **⚙️ 코어 계층** (엔진/최적화) | **`Llama` 모델을 로드**하고, `n_parallel`, `n_batch` 같은 **GPU 튜닝 파라미터를 관리**합니다. (구 `runner.py` 역할) |

이 구조는 **API/서비스/LLM 엔진**을 분리하여 **테스트, 유지보수, 성능 튜닝**을 쉽게 할 수 있도록 설계되었습니다.

## 참고

- 모델: [google/gemma-3-1b-it-qat-q4_0-gguf](https://huggingface.co/google/gemma-3-1b-it-qat-q4_0-gguf)
- 프레임워크: [FastAPI](https://fastapi.tiangolo.com/)
- 기타: [Docker](https://www.docker.com/), [Hugging Face](https://huggingface.co/)

## 라이선스

본 프로젝트는 MIT 라이선스를 따릅니다.

---

문의: [qixiangme](https://github.com/qixiangme)
