# ADR 001: 자율적 문제 해결을 위한 ReAct Agent Engine 채택

## 1. Status
**Accepted**

## 2. Context (배경)
마이크로서비스 환경에서 발생하는 장애는 단편적이지 않고 연쇄적인 경우가 많습니다. 
예를 들어, "결제 지연"이라는 증상의 원인이 "Redis 캐시 메모리 초과"일 수도 있고, "타사 결제 API 타임아웃"일 수도 있습니다.
단순히 미리 정의된 플레이북(Playbook)을 실행하는 기존의 정적 스크립팅 방식으로는 이러한 복합적인 장애 상황을 유연하게 진단하고 조치하기 어렵습니다. 
따라서, 시스템은 다음과 같은 능력을 갖춰야 합니다.
1. 주어진 목표(예: "결제 서비스의 장애 원인을 찾아 복구해라")를 이해.
2. 해결을 위해 필요한 단계를 스스로 계획(Reasoning).
3. 적절한 도구(인프라 모니터링 API, Ansible 스크립트 실행 등)를 선택하여 행동(Act).
4. 행동의 결과를 관찰(Observation)하고 다음 단계를 수정.

## 3. Decision (결정)
LangChain의 **ReAct (Reason + Act)** 에이전트 아키텍처를 핵심 추론 엔진으로 채택합니다.

- **프레임워크:** LangChain (`create_react_agent`, `AgentExecutor`)
- **LLM Provider:** OpenRouter (GPT-4o, Claude 3.5 Sonnet 등 복합 추론에 능한 모델 활용)
- **도구(Tools):** Python `@tool` 데코레이터를 이용해 인프라 제어 도구(Status Check, Script Generation 등)를 캡슐화하여 에이전트에게 제공.

## 4. Rationale (결정 이유)
- **복합 문제 해결력:** ReAct 패턴은 모델이 단순히 정답을 생성하는 것을 넘어, 생각의 과정(Thought)을 강제함으로써 복잡한 다단계 문제 해결의 성공률을 비약적으로 높입니다.
- **도구 사용의 유연성:** 인프라 환경(Kubernetes, AWS, Ansible)에 맞는 맞춤형 도구를 손쉽게 확장하고 에이전트에 주입할 수 있습니다.
- **가시성 확보:** `AgentExecutor`의 `verbose=True` 설정을 통해 에이전트가 어떤 근거로 어떤 행동을 했는지(Thought -> Action -> Observation) 명확히 추적할 수 있어, 장애 조치 과정의 감사(Audit)가 가능합니다.

## 5. Consequences (결과 및 고려사항)
- **LLM 호출 비용 및 속도:** 매 스텝마다 Thought와 Action을 생성하기 위해 LLM을 반복 호출하므로 지연 시간(Latency)과 토큰 비용이 발생합니다.
- **환각(Hallucination) 리스크:** 잘못된 판단으로 인해 치명적인 인프라 변경(예: 멀쩡한 DB 노드 삭제)을 유발할 위험이 있습니다.
- **Mitigation 전략:** 
  1. 에이전트의 권한을 "진단(Read-only)"과 "조치 스크립트 생성(Generation)"까지만 허용하고, 실제 클러스터 적용(Execution) 전에는 관리자의 승인(Human-in-the-loop)을 거치도록 설계합니다.
  2. RAG(Retrieval-Augmented Generation) 엔진을 결합하여, 사내 검증된 인프라 가이드라인(infra-master-lab docs) 내에서만 사고하도록 컨텍스트를 제한합니다.
