# 🛠️ AI Agent Brain Lab Troubleshooting Guide

본 문서는 `ai-agent-brain-lab` 프로젝트의 핵심 컴포넌트인 ReAct 에이전트와 RAG 엔진 구현 중 발생한 주요 트러블슈팅 사례를 기록합니다.

---

## 1. RAG 엔진: Markdown 문서 인덱싱 누락 (UnstructuredLoader 의존성 이슈)

### 🚨 Problem (증상)
`rag_engine.py`의 `ingest_docs()` 메서드 실행 시, 지정된 경로(`INFRA_DOCS_PATH`)에 명백히 `.md` 파일들이 존재함에도 불구하고 
"No documents found to ingest" 에러가 발생하거나 텍스트가 정상적으로 추출되지 않음.

### 🔍 Cause Analysis (원인 분석)
- LangChain의 `DirectoryLoader`에 `UnstructuredMarkdownLoader` 클래스를 매핑하여 사용 중.
- `unstructured` 라이브러리가 기본적으로 지원하는 포맷 외에 Markdown 파싱을 위해서는 시스템 레벨의 의존성이나 추가 Python 패키지(`unstructured[md]`)가 필요함.
- 패키지 누락으로 인해 로더가 조용히 실패하거나 빈 문자열을 반환함.

### ✅ Solution (해결 방안)
`requirements.txt`에 Markdown 파싱을 위한 명시적 의존성을 추가하고 재설치.

```text
# requirements.txt에 추가
unstructured[md]
markdown
```
또는 가벼운 대안으로 `TextLoader`를 상속받아 직접 마크다운 로더를 구현하여 해결 가능.

---

## 2. ReAct Agent: 파싱 에러 (Parsing Error) 및 무한 루프

### 🚨 Problem (증상)
LLM이 `Thought`, `Action`, `Action Input` 형식을 정확히 지키지 않고 자유로운 텍스트로 응답할 때, 
`AgentExecutor`가 "Could not parse LLM output" 에러를 내뿜으며 중단되거나, 동일한 프롬프트를 계속 재요청하며 무한 루프에 빠짐.

### 🔍 Cause Analysis (원인 분석)
- OpenRouter를 통해 연결된 특정 모델(예: Llama 3 등)이 ReAct 프롬프트 포맷 지침을 완벽하게 따르지 못함.
- `Final Answer:` 구문을 누락하거나, 도구를 호출하지 않고 직접 답을 하려다 포맷이 깨짐.

### ✅ Solution (해결 방안)
`AgentExecutor` 초기화 시 `handle_parsing_errors=True` 옵션을 부여하여 포맷 이탈 시 에이전트가 스스로 정정할 수 있는 기회를 제공.
추가적으로 프롬프트 템플릿의 지시문을 더욱 명확하게 강화함.

```python
# agent_brain.py (해결 스니펫)
return AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    handle_parsing_errors=True # 파싱 에러 발생 시 에러 메시지를 LLM에 전달하여 포맷 수정을 유도
)
```

---

## 3. 로컬 임베딩 속도 저하 및 CPU 점유율 폭주

### 🚨 Problem (증상)
RAG 문서 수집(`ingest_docs`) 단계에서 `HuggingFaceEmbeddings`를 사용할 때 처리 속도가 극도로 느리고 서버 CPU가 100%에 달함.

### 🔍 Cause Analysis (원인 분석)
- `all-MiniLM-L6-v2` 모델이 CPU 전용 환경에서 무거운 병렬 연산을 시도함.
- 로컬 개발 환경(Windows/Mac)에서 PyTorch나 ONNX Runtime이 최적화되지 않아 연산 병목 발생.

### ✅ Solution (해결 방안)
`sentence-transformers` 라이브러리를 최적화하거나, 개발 환경에서는 가벼운 캐싱 레이어를 둠.
(실제 프로덕션에서는 GPU 할당 또는 OpenAI의 `text-embedding-3-small` 같은 외부 API 기반 임베딩 모델로의 전환을 고려)
