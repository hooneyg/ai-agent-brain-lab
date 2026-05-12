package com.hooney.lab.agent.ai.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.stereotype.Service;

/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║         💬 ChatService — LLM 기반 자연어 질의/응답 서비스           ║
 * ║                                                                  ║
 * ║  [클래스 목적]                                                   ║
 * ║  Spring AI의 ChatClient를 활용하여 LLM에게 자연어 질문을 전달하고    ║
 * ║  답변을 받아오는 핵심 서비스입니다.                                  ║
 * ║                                                                  ║
 * ║  [동작 원리]                                                     ║
 * ║  ChatClient.Builder가 application.yml의 AI 설정에 따라              ║
 * ║  적절한 LLM 프로바이더(Ollama, HuggingFace 등)를 자동 주입합니다.    ║
 * ║  개발자는 프로바이더 교체 시 application.yml만 수정하면 됩니다.       ║
 * ║                                                                  ║
 * ║  [시스템 프롬프트]                                                ║
 * ║  인프라 엔지니어 전문가 페르소나를 부여하여                          ║
 * ║  인프라 관련 질문에 최적화된 답변을 유도합니다.                       ║
 * ║                                                                  ║
 * ║  @author Hooney — AI FullStack Developer                         ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */
@Service
public class ChatService {

    private static final Logger log = LoggerFactory.getLogger(ChatService.class);

    /** Spring AI ChatClient — LLM 호출을 추상화하는 고수준 클라이언트 */
    private final ChatClient chatClient;

    /**
     * 시스템 프롬프트 — LLM의 역할(페르소나)을 정의한다.
     *
     * 이 프롬프트는 모든 대화의 시작에 주입되어 LLM이
     * "인프라 전문 시니어 엔지니어"로서 답변하도록 유도한다.
     * 한국어 답변을 강제하여 일관된 사용자 경험을 보장한다.
     */
    private static final String SYSTEM_PROMPT = """
            당신은 인프라 관리 전문 시니어 엔지니어입니다.
            다음 규칙을 엄격히 따르세요:
            1. 한국어로 답변하세요.
            2. 기술 용어는 영어 원문을 병기하세요. (예: 로드밸런서(Load Balancer))
            3. 답변은 구조적으로 작성하세요. (제목, 원인 분석, 해결 방안, 예시 코드)
            4. 불확실한 정보는 "확인 필요"라고 명시하세요.
            """;

    /**
     * ChatService 생성자.
     *
     * @param chatClientBuilder Spring AI가 자동 주입하는 ChatClient.Builder.
     *                          application.yml의 AI 설정에 따라 적절한
     *                          ChatModel(Ollama, HuggingFace, OpenAI 등)이 연결됩니다.
     *
     *                          빌더 패턴으로 시스템 프롬프트를 사전 설정하여,
     *                          모든 chat() 호출에 자동으로 적용되도록 합니다.
     */
    public ChatService(ChatClient.Builder chatClientBuilder) {
        this.chatClient = chatClientBuilder
                .defaultSystem(SYSTEM_PROMPT)
                .build();
        log.info("✅ ChatService initialized with system prompt.");
    }

    /**
     * LLM에게 자연어 질문을 전달하고 답변을 받아옵니다.
     *
     * @param message 사용자의 질문 메시지.
     *                예: "Docker 컨테이너의 OOM Killed 에러 원인이 뭐야?"
     * @return LLM이 생성한 자연어 답변 문자열.
     * @throws RuntimeException LLM 호출 실패 시 (네트워크, API Key 오류 등).
     */
    public String chat(String message) {
        log.info("💬 [ChatService] Processing query: {}", message);
        try {
            // ChatClient.prompt()로 대화를 시작하고,
            // user()로 사용자 메시지를 추가한 후,
            // call()로 LLM을 호출하여 답변을 받아온다.
            String response = chatClient
                    .prompt()
                    .user(message)
                    .call()
                    .content();
            log.info("✅ [ChatService] Response received successfully.");
            return response;
        } catch (Exception e) {
            log.error("❌ [ChatService] LLM call failed: {}", e.getMessage());
            throw new RuntimeException("LLM 호출에 실패했습니다: " + e.getMessage(), e);
        }
    }
}
