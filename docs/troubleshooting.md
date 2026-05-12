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

---

## 4. Spring AI: BOM 버전 충돌 (agent-ai-spring)

### 🚨 Problem (증상)
`agent-ai-spring` 모듈의 `./gradlew build` 실행 시 Spring AI 관련 의존성 해결(resolution) 실패.
`Could not resolve org.springframework.ai:spring-ai-starter-model-ollama` 에러 발생.

### 🔍 Cause Analysis (원인 분석)
- Spring AI BOM 버전과 Spring Boot 버전 간 호환성 불일치.
- Spring AI 1.0.x는 Spring Boot 3.4+ 이상을 요구하지만, 프로젝트가 다른 버전을 사용 중일 수 있음.
- Maven Central이 아닌 Spring Milestones 저장소가 누락되었을 가능성.

### ✅ Solution (해결 방안)
```groovy
// build.gradle
dependencies {
    // BOM을 platform()으로 선언하여 버전 통합 관리
    implementation platform('org.springframework.ai:spring-ai-bom:1.0.7')
    implementation 'org.springframework.ai:spring-ai-starter-model-ollama'  // 버전 생략
}

// 필요 시 Spring Milestones 저장소 추가
repositories {
    mavenCentral()
    maven { url 'https://repo.spring.io/milestone' }
}
```

---

## 5. Ollama 서버 연결 실패 (Connection Refused)

### 🚨 Problem (증상)
`agent-ai-spring` 또는 `agent-core`에서 Ollama 로컬 서버 호출 시
`Connection refused: localhost:11434` 에러 발생.

### 🔍 Cause Analysis (원인 분석)
1. Ollama 서버가 실행되지 않은 상태에서 AI 요청을 시도함.
2. Windows 방화벽이 11434 포트를 차단하고 있을 수 있음.
3. Docker 컨테이너 내에서 `localhost`가 호스트 머신을 가리키지 않음.

### ✅ Solution (해결 방안)
```bash
# 1. Ollama 서버 실행 확인
ollama serve
# 또는 백그라운드 실행
ollama serve &

# 2. 포트 사용 확인
netstat -ano | findstr :11434

# 3. Docker 환경에서는 host.docker.internal 사용
# application.yml:
#   spring.ai.ollama.base-url: http://host.docker.internal:11434
```

---

## 6. Spring AI Embedding 차원 불일치 (VectorStore 에러)

### 🚨 Problem (증상)
RAG 인덱싱 후 검색 시 `Embedding dimension mismatch` 또는
`Vector size does not match` 에러 발생.

### 🔍 Cause Analysis (원인 분석)
- 인덱싱 시 사용한 임베딩 모델과 검색 시 사용한 모델이 다름.
- 예: 인덱싱은 `nomic-embed-text`(768차원), 검색은 `all-minilm`(384차원)으로 수행.
- SimpleVectorStore의 이전 데이터가 다른 차원의 벡터를 포함.

### ✅ Solution (해결 방안)
1. 인덱싱과 검색에 반드시 동일한 임베딩 모델을 사용합니다.
2. 모델 변경 시 기존 VectorStore 데이터를 삭제하고 재인덱싱합니다.
3. `application.yml`에서 임베딩 모델을 한 곳에서 관리합니다.

```yaml
spring:
  ai:
    ollama:
      embedding:
        model: nomic-embed-text  # 인덱싱/검색 모두 이 모델 사용
```

---

## 7. Docker 빌드 시 Gradle Wrapper 권한 에러

### 🚨 Problem (증상)
`docker-compose up --build` 실행 시 Java 모듈 빌드 과정에서
`Permission denied: ./gradlew` 에러 발생.

### 🔍 Cause Analysis (원인 분석)
- Windows에서 `git clone`한 경우 `gradlew` 파일의 실행 권한(`+x`)이 누락될 수 있음.
- Docker 빌드 컨텍스트로 복사된 파일이 Windows 파일 시스템의 권한을 그대로 유지함.

### ✅ Solution (해결 방안)
```bash
# 1. 호스트에서 실행 권한 부여
git update-index --chmod=+x gradlew
git commit -m "fix: gradlew 실행 권한 추가"

# 2. 또는 Dockerfile에서 직접 권한 부여 (이미 적용됨)
# RUN chmod +x gradlew
```

---

## 8. Docker 컨테이너 간 통신 실패 (서비스명 해석 불가)

### 🚨 Problem (증상)
`agent-orchestrator` 컨테이너에서 `agent-core` 호출 시
`UnknownHostException: agent-core` 또는 `Connection refused` 에러 발생.

### 🔍 Cause Analysis (원인 분석)
1. `docker-compose.yml`의 네트워크 설정이 누락되어 각 서비스가 서로 다른 네트워크에 배치됨.
2. `application.yml`에서 `localhost`를 사용하고 있어 Docker 서비스명으로 변환되지 않음.
3. 의존 서비스가 아직 기동 중(Health Check 미통과)인 상태에서 요청을 시도함.

### ✅ Solution (해결 방안)
```yaml
# 1. docker-compose.yml에서 모든 서비스가 같은 네트워크를 사용하도록 설정
networks:
  agent-network:
    driver: bridge

# 2. application-docker.yml에서 서비스명 사용
agent:
  core:
    url: http://agent-core:8000   # localhost → 서비스명

# 3. depends_on + healthcheck로 기동 순서 보장
depends_on:
  agent-core:
    condition: service_healthy
```

---

## 9. Ollama 모델 다운로드 타임아웃 (docker-compose)

### 🚨 Problem (증상)
`docker-compose up` 실행 시 `ollama-init` 컨테이너가 모델 다운로드 중 타임아웃으로 실패.
또는 디스크 공간 부족으로 모델 Pull이 중단됨.

### 🔍 Cause Analysis (원인 분석)
- `llama3.1` 모델은 약 4.7GB, `nomic-embed-text`는 약 274MB의 다운로드가 필요함.
- 네트워크 대역폭이 낮거나 Docker 디스크 할당량이 부족한 경우 실패.
- WSL2 환경에서 기본 가상 디스크 크기(256GB)를 초과하면 다운로드 불가.

### ✅ Solution (해결 방안)
```bash
# 1. Docker에 모델 저장 전 호스트에서 사전 다운로드
ollama pull llama3.1
ollama pull nomic-embed-text

# 2. Docker Desktop 디스크 할당량 확인
# Settings > Resources > Disk image size 를 최소 50GB 이상으로 설정

# 3. 경량 모델로 대체 (테스트 시)
# docker-compose.yml의 ollama-init에서 모델 변경:
# ollama pull phi3:mini      # 약 2.3GB — 가벼운 대안
# ollama pull nomic-embed-text  # 임베딩은 가벼우므로 유지
```

