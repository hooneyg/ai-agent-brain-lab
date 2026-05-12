# ╔══════════════════════════════════════════════════════════════════╗
# ║         🐍 Dockerfile — AI Agent Core (Python FastAPI)            ║
# ║                                                                  ║
# ║  [이미지 목적]                                                   ║
# ║  LangChain ReAct 에이전트 + RAG 엔진을 실행하는 Python API 서버.   ║
# ║  FastAPI + Uvicorn 기반으로 포트 8000에서 서비스됩니다.             ║
# ║                                                                  ║
# ║  [빌드 방법]                                                     ║
# ║  docker build -t agent-core ./agent-core                         ║
# ║                                                                  ║
# ║  [실행 방법]                                                     ║
# ║  docker run -p 8000:8000 --env-file .env agent-core              ║
# ║                                                                  ║
# ║  @author Hooney — AI FullStack Developer                         ║
# ╚══════════════════════════════════════════════════════════════════╝

# ──────────────────────────────────────────────────────────────────
# Stage 1: Base 이미지 선택
# Python 3.11-slim: 경량 이미지 (약 130MB vs full 900MB)
# slim 버전은 불필요한 도구(gcc, make 등)를 제외하여 이미지 크기를 최소화한다.
# ──────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS base

# 메타데이터 라벨 — 이미지 관리 및 추적에 사용
LABEL maintainer="Hooney <hooneyg@github.com>"
LABEL description="AI Agent Brain Core — ReAct Agent + RAG Engine"
LABEL version="1.0.0"

# ──────────────────────────────────────────────────────────────────
# Python 환경 최적화
# ──────────────────────────────────────────────────────────────────
# PYTHONDONTWRITEBYTECODE=1: .pyc 파일 생성 방지 (컨테이너에선 불필요)
# PYTHONUNBUFFERED=1: stdout/stderr 버퍼링 비활성화 → 로그 즉시 출력
# 컨테이너 환경에서는 버퍼링 시 로그가 누락될 수 있으므로 반드시 설정해야 한다.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 작업 디렉토리 설정
WORKDIR /app

# ──────────────────────────────────────────────────────────────────
# 의존성 설치 (캐싱 최적화)
# requirements.txt를 먼저 복사하여 Docker 레이어 캐싱을 활용한다.
# 코드 변경 시에도 의존성 레이어가 캐시되어 빌드 시간이 단축된다.
# ──────────────────────────────────────────────────────────────────
COPY requirements.txt .

# pip 업그레이드 후 의존성 설치
# --no-cache-dir: pip 캐시 비활성화 → 이미지 크기 절감
# --timeout=300: HuggingFace 모델 다운로드에 시간이 걸릴 수 있으므로 타임아웃 연장
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --timeout=300 -r requirements.txt

# ──────────────────────────────────────────────────────────────────
# 애플리케이션 코드 복사
# ──────────────────────────────────────────────────────────────────
COPY . .

# RAG 벡터 저장소 영속화 디렉토리 생성
# Docker 볼륨 마운트 포인트로 사용 가능
RUN mkdir -p /app/data/chromadb

# ──────────────────────────────────────────────────────────────────
# 컨테이너 실행 설정
# ──────────────────────────────────────────────────────────────────
# 서비스 포트 노출
EXPOSE 8000

# Health Check — 30초마다 서버 상태를 확인하여 컨테이너 헬스 관리
# Docker Compose의 depends_on.condition: service_healthy와 연동됨
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# Uvicorn으로 FastAPI 서버 실행
# --host 0.0.0.0: 컨테이너 외부에서 접근 가능하도록 모든 인터페이스에 바인딩
# --workers 2: 멀티 워커로 동시 요청 처리 (CPU 코어 수에 따라 조정)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
