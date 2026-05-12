package com.hooney.lab.agent.adapter.out.web;

import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.Map;

/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║         🧠 AgentClient — Java-Python 비동기 통신 브릿지            ║
 * ║                                                                  ║
 * ║  [클래스 목적]                                                   ║
 * ║  Python FastAPI 기반 AI Agent Core와의 비동기 REST 통신을 담당합니다.║
 * ║  WebClient(논블로킹)를 사용하여 AI 추론 요청을 전달하고              ║
 * ║  응답을 비동기적으로 수신합니다.                                     ║
 * ║                                                                  ║
 * ║  [아키텍처 위치]                                                  ║
 * ║  Hexagonal Architecture의 Outbound Adapter (adapter/out/web)      ║
 * ║  → 외부 시스템(Python AI Core)과의 통신을 캡슐화                    ║
 * ║                                                                  ║
 * ║  [통신 대상]                                                     ║
 * ║  - POST /ask    → AI 에이전트 질의 (ReAct 추론 실행)               ║
 * ║  - POST /ingest → RAG 지식 베이스 업데이트 요청                    ║
 * ║                                                                  ║
 * ║  [향후 개선 사항]                                                 ║
 * ║  - Timeout/Retry/Circuit Breaker 패턴 적용 (Resilience4j)         ║
 * ║  - baseUrl을 환경 변수(application.yml)에서 주입받도록 개선          ║
 * ║                                                                  ║
 * ║  @author Hooney — AI FullStack Developer                         ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */
@Component
public class AgentClient {

    /** WebClient: Spring WebFlux의 논블로킹 HTTP 클라이언트 */
    private final WebClient webClient;

    /**
     * AgentClient 생성자.
     *
     * Python FastAPI 서버(agent-core)의 기본 URL로 WebClient를 초기화합니다.
     *
     * TODO: baseUrl을 application.yml의 설정값(${agent.core.url})으로
     *       외부 주입받도록 리팩토링 필요.
     *       현재는 로컬 개발 환경 기준으로 하드코딩되어 있음.
     *       Docker 환경에서는 "http://agent-core:8000"으로 변경해야 합니다.
     */
    public AgentClient() {
        // Python FastAPI 서버 주소로 WebClient 초기화
        // 기본 포트: 8000 (agent-core/main.py의 uvicorn 설정)
        this.webClient = WebClient.builder()
                .baseUrl("http://localhost:8000")
                .build();
    }

    /**
     * AI 에이전트에게 질문을 전달하고 답변을 비동기로 받아옵니다.
     *
     * Python agent-core의 POST /ask 엔드포인트를 호출합니다.
     * WebClient의 Mono 반환으로 논블로킹 처리되어,
     * AI 추론 대기 중에도 서버 스레드가 블로킹되지 않습니다.
     *
     * @param query 사용자의 자연어 질문.
     *              예: "결제 서비스 노드의 장애 원인을 분석해줘"
     * @return Mono&lt;Map&gt; AI 에이전트의 추론 결과를 담은 비동기 응답.
     *         응답 구조: { "query": "...", "answer": "...", "metadata": {...} }
     */
    public Mono<Map> askAgent(String query) {
        return this.webClient.post()
                .uri("/ask")
                // 요청 바디: { "query": "사용자 질문" }
                .bodyValue(Map.of("query", query))
                .retrieve()
                .bodyToMono(Map.class);
    }

    /**
     * AI 에이전트에게 RAG 지식 베이스 업데이트(Ingestion)를 요청합니다.
     *
     * Python agent-core의 POST /ingest 엔드포인트를 호출합니다.
     * 인덱싱은 agent-core 내부에서 백그라운드로 처리되므로 즉시 응답됩니다.
     *
     * @return Mono&lt;String&gt; 인덱싱 시작 확인 메시지.
     *         예: "Knowledge ingestion started in background."
     */
    public Mono<String> requestIngestion() {
        return this.webClient.post()
                .uri("/ingest")
                .retrieve()
                .bodyToMono(Map.class)
                .map(res -> res.get("message").toString());
    }
}
