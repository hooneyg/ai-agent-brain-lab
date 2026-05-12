# ╔══════════════════════════════════════════════════════════════════╗
# ║         🐍 main.py — AI Agent Core API 서버 엔트리포인트          ║
# ║                                                                  ║
# ║  [파일 목적]                                                     ║
# ║  FastAPI 기반 REST API 서버. 외부에서 AI 에이전트의 추론 기능에     ║
# ║  접근할 수 있는 HTTP 인터페이스를 제공합니다.                       ║
# ║                                                                  ║
# ║  [제공 API]                                                      ║
# ║  GET  /        — 서버 상태 확인 (Health Check)                    ║
# ║  POST /ingest  — RAG 지식 베이스 업데이트 (문서 인덱싱)            ║
# ║  POST /ask     — AI 에이전트에게 자연어 질의 수행                   ║
# ║                                                                  ║
# ║  [작성자] Hooney — AI FullStack Developer                        ║
# ╚══════════════════════════════════════════════════════════════════╝

import logging
import os
import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from rag_engine import RagEngine
from agent_brain import AgentBrain
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드 (API Key, 모델명 등 민감 정보 분리)
load_dotenv()

# 전역 로깅 설정 — 모든 모듈의 로그를 통일된 형식으로 출력
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("API-Server")

# FastAPI 인스턴스 — Swagger UI는 /docs 에서 확인 가능
app = FastAPI(
    title="AI Agent Brain Core",
    description="Autonomous Reasoning Engine for Infrastructure Management",
    version="1.0.0"
)

# RAG 지식 베이스의 소스 문서 경로 (환경 변수로 오버라이드 가능)
INFRA_DOCS_PATH = os.getenv("INFRA_DOCS_PATH", "d:/works/20260508/infra-master-lab")

# 서버 시작 시 1회 초기화 — "Fail Fast" 원칙: 불완전한 상태로 요청 받지 않음
try:
    rag = RagEngine(docs_path=INFRA_DOCS_PATH)
    brain = AgentBrain(rag_engine=rag)
    logger.info("✅ RAG and Agent Brain initialized successfully.")
except Exception as e:
    logger.error(f"❌ Failed to initialize core components: {str(e)}")
    raise

class QueryRequest(BaseModel):
    """AI 에이전트 질의 요청 모델. query 필드에 자연어 질문을 담는다."""
    query: str

@app.get("/")
async def read_root():
    """서버 및 하위 컴포넌트(RAG, Agent) 상태 확인 — Health Check 용도"""
    return {"status": "online", "components": {"rag": "active", "agent": "active"}}

@app.post("/ingest")
async def ingest_knowledge(background_tasks: BackgroundTasks):
    """
    RAG 지식 베이스 업데이트 — 문서를 벡터 임베딩으로 변환하여 ChromaDB에 저장.
    대량 문서 인덱싱은 수 분 소요 가능하므로 BackgroundTasks로 비동기 처리한다.
    """
    logger.info("📥 Knowledge ingestion requested.")
    background_tasks.add_task(rag.ingest_docs)
    return {"message": "Knowledge ingestion started in background."}

@app.post("/ask")
async def ask_agent(request: QueryRequest):
    """
    AI 에이전트에게 질의 수행.
    흐름: 요청 검증 → RAG 컨텍스트 검색 → ReAct 추론 → 최종 답변 반환.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    logger.info(f"❓ User query received: {request.query}")
    response = brain.run(request.query)
    return {
        "query": request.query,
        "answer": response.get("output", "결과를 생성하지 못했습니다."),
        "metadata": {"engine": "ReAct Reasoning", "knowledge_source": INFRA_DOCS_PATH}
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Starting server on port {port}")
    # host="0.0.0.0": Docker 환경에서 외부 접근을 위해 모든 인터페이스에 바인딩
    uvicorn.run(app, host="0.0.0.0", port=port)
