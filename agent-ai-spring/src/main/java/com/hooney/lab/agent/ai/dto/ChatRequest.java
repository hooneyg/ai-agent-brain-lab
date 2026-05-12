package com.hooney.lab.agent.ai.dto;

import jakarta.validation.constraints.NotBlank;

/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║         📨 ChatRequest — LLM 채팅 요청 DTO                       ║
 * ║                                                                  ║
 * ║  [용도] POST /api/v1/ai/chat 엔드포인트의 요청 바디 모델.           ║
 * ║  사용자의 자연어 질문을 담아 LLM에게 전달합니다.                      ║
 * ║                                                                  ║
 * ║  @author Hooney — AI FullStack Developer                         ║
 * ╚══════════════════════════════════════════════════════════════════╝
 *
 * @param message 사용자의 질문 메시지. 빈 문자열 불가(@NotBlank).
 *                예: "컨테이너 OOM 발생 시 대응 방법을 알려줘"
 */
public record ChatRequest(
        @NotBlank(message = "메시지는 비어있을 수 없습니다.")
        String message
) {}
