# ADR-002: Spring AI + HuggingFace Java-native AI 통합

## 상태 (Status)
✅ **채택 (Accepted)** — 2026-05-13

## 맥락 (Context)
현재 AI Agent Brain Lab은 Python 기반의 agent-core(LangChain + FastAPI)가 유일한 AI 처리 엔진입니다.
Java agent-orchestrator는 단순히 Python 서버를 HTTP로 호출하는 브릿지 역할만 수행합니다.

### 발생한 문제
1. **단일 장애점 (SPOF):** Python 서버 장애 시 전체 AI 기능이 중단됨
2. **기술 편중:** AI 관련 코드가 Python에만 집중되어 Java 개발자의 참여가 제한적
3. **운영 복잡도:** 2개 런타임(JVM + Python)을 반드시 동시에 관리해야 함
4. **포트폴리오 관점:** Spring Boot 생태계 내에서 AI를 다루는 역량 시연 필요

## 결정 (Decision)
Spring AI 프레임워크를 활용하여 **agent-ai-spring** 모듈을 신설하고,
Java-native로 LLM Chat, Embedding, RAG 파이프라인을 구현한다.

### 기술 선택 근거

| 항목 | 선택 | 대안 | 선택 이유 |
|------|------|------|-----------|
| AI 프레임워크 | Spring AI 1.0.7 | LangChain4J, DJL | Spring 생태계 공식 지원, BOM 통합 관리 |
| LLM 프로바이더 | HuggingFace + Ollama | OpenAI 직접 호출 | 무료 오픈소스 모델 활용, API Key 비용 절감 |
| 벡터 저장소 | SimpleVectorStore | pgvector, Weaviate | 개발 환경 제로 설정, 프로덕션 시 교체 용이 |
| 임베딩 모델 | nomic-embed-text (Ollama) | OpenAI text-embedding-3 | 로컬 무료 실행, 768차원 충분한 정밀도 |

### API Key 전략

현재 API Key를 보유하지 않으므로, 다음 2가지 전략을 모두 지원합니다:
- **로컬 모드 (기본):** Ollama를 통한 오픈소스 모델 로컬 실행 — API Key 불필요
- **클라우드 모드:** HuggingFace/OpenAI API Key 설정 시 자동 전환

```yaml
# application.yml 플레이스홀더 예시
spring.ai.huggingface.chat.api-key: ${HUGGINGFACE_API_KEY:[HUGGINGFACE_API_KEY]}
spring.ai.ollama.base-url: ${OLLAMA_BASE_URL:http://localhost:11434}
```

## 결과 (Consequences)

### 긍정적 효과
- **이중화:** Python 장애 시에도 Java에서 기본적인 AI 질의/응답 가능
- **개발자 접근성:** Java 개발자가 Spring 패턴으로 AI 기능을 다룰 수 있음
- **포트폴리오 강화:** Spring AI + HuggingFace 실무 경험 시연
- **비용 절감:** Ollama 로컬 모드로 개발/테스트 시 API 비용 제로

### 부정적 효과
- **중복:** Python agent-core와 기능이 일부 중복됨
- **학습 비용:** Spring AI 프레임워크 학습 필요
- **모듈 증가:** 관리해야 할 서비스가 2개에서 3개로 증가

### 완화 조치
- 각 모듈의 역할을 명확히 분리:
  - `agent-core`: 복잡한 ReAct 추론 (다단계 도구 활용)
  - `agent-ai-spring`: 단순 Chat, Embedding, RAG (Spring 생태계 통합)
- Docker Compose로 3개 서비스를 일괄 관리

## 참고 (References)
- [Spring AI 공식 문서](https://docs.spring.io/spring-ai/reference/)
- [ADR-001: ReAct Agent Engine 선택](./ADR-001-react-agent-engine.md)
- [로컬 AI 모델 가이드](../../Github_Renewal/ai-agent-brain-lab/01_Local_AI_Model_Guide.md)
