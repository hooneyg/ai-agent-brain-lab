# 🧠 AI Agent Brain Lab: The Era of Autonomous Reasoning

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-Enabled-00A67E?style=for-the-badge&logo=chainlink&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-High_Performance-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenRouter-API-blue?style=for-the-badge&logo=openai&logoColor=white" />
</div>

---

## 🏛️ Project Overview
**AI Agent Brain Lab**은 마이크로서비스 생태계에 자율적인 사고 능력을 부여하는 **지능형 에이전트의 중추**를 개발하는 프로젝트입니다. `infra-master-lab`에서 구축한 인프라를 스스로 분석하고, 자연어 질의를 통해 인프라 상태를 진단하며 조치하는 **Self-Healing AI**를 목표로 합니다.

---

## 📐 System Architecture

```mermaid
graph TD
    User([User / Developer]) <--> API[FastAPI Server]
    
    subgraph "Agent Brain Core"
        API <--> Agent[ReAct Agent Engine]
        Agent <--> RAG[RAG Retrieval Engine]
        Agent <--> Tools[Infrastructure Tools]
    end
    
    subgraph "Knowledge & LLM"
        RAG --> VectorDB[(ChromaDB)]
        VectorDB -- Local Embedding --> HF[HuggingFace: all-MiniLM-L6-v2]
        Agent -- LLM Request --> OR[OpenRouter API]
    end
    
    subgraph "External Targets"
        Tools --> Infra[(infra-master-lab)]
        Infra --> K8S[Kubernetes Cluster]
        Infra --> Ansible[Ansible Playbooks]
    end
```

---

## ✨ Key Features
- **Autonomous Reasoning**: ReAct(Reason + Act) 패턴을 통한 복합 문제 해결 및 계획 수립
- **Context-Aware RAG**: 로컬 임베딩 모델을 활용한 고효율 인프라 기술 문서 기반 검색
- **Multi-Tool Integration**: 인프라 상태 조회 및 복구 스크립트 생성을 위한 커스텀 도구 지원
- **Clean Architecture**: 확장성을 고려한 계층형 구조 및 정밀한 로깅 시스템

---

## 🛠️ Technology Stack
- **Framework**: FastAPI (Python 3.11+)
- **LLM Orchestration**: LangChain, LangChain-OpenAI
- **LLM Provider**: OpenRouter (GPT-4o, Claude 3.5 Sonnet 등 가변 모델 지원)
- **Vector Store**: ChromaDB
- **Embeddings**: HuggingFace (Local Execution)

---

## 🚀 Quick Start

### 1. Environment Setup
```bash
cd agent-core
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configuration (.env)
```env
OPENROUTER_API_KEY=your_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-4o
INFRA_DOCS_PATH=d:/works/20260508/infra-master-lab
```

### 3. Running the Server
```bash
python main.py
```

### 4. API Testing
- **Ingest**: `curl -X POST http://localhost:8000/ingest`
- **Ask**: `curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d "{\"query\": \"인프라 노드 상태 점검해줘.\"}"`

---

## 📝 License
This project is licensed under the MIT License.
**Designed with Passion by Hooney** 🚀
