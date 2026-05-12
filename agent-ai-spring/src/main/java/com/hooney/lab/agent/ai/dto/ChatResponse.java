package com.hooney.lab.agent.ai.dto;

/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║         📬 ChatResponse — LLM 채팅 응답 DTO                       ║
 * ║                                                                  ║
 * ║  [용도] POST /api/v1/ai/chat 엔드포인트의 응답 바디 모델.           ║
 * ║  LLM이 생성한 답변과 메타데이터를 클라이언트에 전달합니다.            ║
 * ║                                                                  ║
 * ║  @author Hooney — AI FullStack Developer                         ║
 * ╚══════════════════════════════════════════════════════════════════╝
 *
 * @param answer  LLM이 생성한 자연어 답변.
 * @param model   사용된 LLM 모델명. 예: "llama3.1", "gpt-4o"
 * @param engine  응답을 생성한 엔진 식별자. 예: "spring-ai-ollama"
 */
public record ChatResponse(
        String answer,
        String model,
        String engine
) {}
