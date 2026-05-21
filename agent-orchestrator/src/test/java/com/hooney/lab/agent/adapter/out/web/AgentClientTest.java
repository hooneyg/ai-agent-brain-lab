package com.hooney.lab.agent.adapter.out.web;

import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import reactor.test.StepVerifier;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.TimeUnit;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * 🧪 AgentClientTest (WebClient 통신 회복성 및 타임아웃 통합 테스트)
 * 
 * [검증 포인트]
 * 1. AI 서버 정상 응답 시 메시지가 정상적으로 파싱되어 리턴되는가?
 * 2. AI 서버가 10초 이상 응답을 주지 않을 때(Timeout) Fallback 메시지를 올바르게 리턴하는가?
 * 3. AI 서버 오류(500 Internal Server Error 등) 시 장애 전파를 막고 우아한 Fallback 응답을 반환하는가?
 */
class AgentClientTest {

    private MockWebServer mockWebServer;
    private AgentClient agentClient;

    @BeforeEach
    void setUp() throws IOException {
        mockWebServer = new MockWebServer();
        mockWebServer.start();

        agentClient = new AgentClient();
        // WebClient의 baseUrl을 동적으로 실행 중인 MockWebServer의 주소로 덮어씌웁니다.
        WebClient mockWebClient = WebClient.builder()
                .baseUrl(mockWebServer.url("/").toString())
                .build();
        ReflectionTestUtils.setField(agentClient, "webClient", mockWebClient);
    }

    @AfterEach
    void tearDown() {
        try {
            if (mockWebServer != null) {
                mockWebServer.shutdown();
            }
        } catch (IOException e) {
            // 타임아웃 테스트 등으로 인해 지연 상태인 소켓이 강제 종료되면서 발생하는 예외는 무시합니다.
        }
    }


    @Test
    @DisplayName("정상적인 askAgent 요청에 대해 결과를 파싱하여 반환하는지 테스트")
    void askAgent_success_test() {
        // Given: Mock AI API 응답 설정
        mockWebServer.enqueue(new MockResponse()
                .setHeader("Content-Type", "application/json")
                .setBody("{\"query\": \"Hello\", \"answer\": \"Hi, I am Agent.\", \"metadata\": {}}"));

        // When: AI 에이전트 질문 전송
        Mono<Map> responseMono = agentClient.askAgent("Hello");

        // Then: 정상적인 응답 파싱 여부 검증
        StepVerifier.create(responseMono)
                .assertNext(res -> {
                    assertThat(res.get("query")).isEqualTo("Hello");
                    assertThat(res.get("answer")).isEqualTo("Hi, I am Agent.");
                })
                .verifyComplete();
    }

    @Test
    @DisplayName("API 서버 응답 지연 시 타임아웃(Timeout)이 발생하고 Fallback 답변을 주는지 테스트")
    void askAgent_timeout_fallback_test() {
        // Given: 15초의 지연시간을 가진 응답 대기 상태 구축 (WebClient 타임아웃 한도는 10초)
        mockWebServer.enqueue(new MockResponse()
                .setBodyDelay(15, TimeUnit.SECONDS)
                .setHeader("Content-Type", "application/json")
                .setBody("{\"query\": \"Hello\", \"answer\": \"Too late...\", \"metadata\": {}}"));

        // When: AI 에이전트 질문 전송
        Mono<Map> responseMono = agentClient.askAgent("Hello");

        // Then: 타임아웃 예외가 정상 캡처되고 타임아웃 안내 문구가 포함된 Fallback이 오는지 검증
        StepVerifier.create(responseMono)
                .assertNext(res -> {
                    assertThat(res.get("query")).isEqualTo("Hello");
                    assertThat(res.get("answer").toString()).contains("타임아웃이 발생했습니다");
                    assertThat(((Map) res.get("metadata")).get("error")).isEqualTo("timeout");
                })
                .verifyComplete();
    }

    @Test
    @DisplayName("서버 500 에러 발생 시 Fallback 에러 응답을 주는지 테스트")
    void askAgent_server_error_fallback_test() {
        // Given: 서버 내부 에러 응답
        mockWebServer.enqueue(new MockResponse().setResponseCode(500));

        // When: AI 에이전트 질문 전송
        Mono<Map> responseMono = agentClient.askAgent("Hello");

        // Then: 에러 감지 후 우아하게 Fallback 처리가 되는지 검증
        StepVerifier.create(responseMono)
                .assertNext(res -> {
                    assertThat(res.get("query")).isEqualTo("Hello");
                    assertThat(res.get("answer").toString()).contains("에러가 발생했습니다");
                    assertThat(((Map) res.get("metadata")).get("error")).isEqualTo("failed");
                })
                .verifyComplete();
    }
}
