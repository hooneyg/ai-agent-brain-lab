# ╔══════════════════════════════════════════════════════════════════╗
# ║         🐍 main.py (AI Agent Core Entry Point)                  ║
# ║                                                                  ║
# ║  [코드 역할]                                                     ║
# ║  1. LangChain 에이전트와의 인터페이스 제공                         ║
# ║  2. 추론 결과 및 RAG 컨텍스트 반환                                 ║
# ╚══════════════════════════════════════════════════════════════════╝

import logging
import os
import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from rag_engine import RagEngine
from agent_brain import AgentBrain
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("API-Server")

app = FastAPI(
    title="AI Agent Brain Core",
    description="Autonomous Reasoning Engine for Infrastructure Management",
    version="1.0.0"
)

# 설정 정보 (환경 변수 우선)
INFRA_DOCS_PATH = os.getenv("INFRA_DOCS_PATH", "d:/works/20260508/infra-master-lab")

# RAG 및 에이전트 브레인 초기화
try:
    rag = RagEngine(docs_path=INFRA_DOCS_PATH)
    brain = AgentBrain(rag_engine=rag)
    logger.info("✅ RAG and Agent Brain initialized successfully.")
except Exception as e:
    logger.error(f"❌ Failed to initialize core components: {str(e)}")
    raise

class QueryRequest(BaseModel):
    query: str

@app.get("/")
async def read_root():
    """서버 상태 확인"""
    return {
        "status": "online",
        "components": {
            "rag": "active",
            "agent": "active"
        }
    }

@app.post("/ingest")
async def ingest_knowledge(background_tasks: BackgroundTasks):
    """지식 베이스 업데이트 (백그라운드)"""
    logger.info("📥 Knowledge ingestion requested.")
    background_tasks.add_task(rag.ingest_docs)
    return {"message": "Knowledge ingestion started in background."}

@app.post("/ask")
async def ask_agent(request: QueryRequest):
    """에이전트에게 질의 수행"""
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    logger.info(f"❓ User query received: {request.query}")
    response = brain.run(request.query)
    
    return {
        "query": request.query,
        "answer": response.get("output", "결과를 생성하지 못했습니다."),
        "metadata": {
            "engine": "ReAct Reasoning",
            "knowledge_source": INFRA_DOCS_PATH
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
