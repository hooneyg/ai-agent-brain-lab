package com.hooney.lab.agent.adapter.out.web;

import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.Map;

/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║         🧠 AgentClient (Java-Python Bridge)                     ║
 * ║                                                                  ║
 * ║  [코드 역할]                                                     ║
 * ║  1. Python 기반 AI Agent Core와 비동기 REST 통신 수행             ║
 * ║  2. 사용자 질의 전달 및 AI 추론 결과 수신                          ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */
@Component
public class AgentClient {

    private final WebClient webClient;

    public AgentClient() {
        // Python FastAPI 서버 주소로 WebClient 초기화
        this.webClient = WebClient.builder()
                .baseUrl("http://localhost:8000")
                .build();
    }

    /**
     * AI 에이전트에게 질문을 던지고 답변을 받아옵니다.
     */
    public Mono<Map> askAgent(String query) {
        return this.webClient.post()
                .uri("/ask")
                .bodyValue(Map.of("query", query))
                .retrieve()
                .bodyToMono(Map.class);
    }

    /**
     * AI 에이전트에게 지식 학습(Ingestion)을 요청합니다.
     */
    public Mono<String> requestIngestion() {
        return this.webClient.post()
                .uri("/ingest")
                .retrieve()
                .bodyToMono(Map.class)
                .map(res -> res.get("message").toString());
    }
}
