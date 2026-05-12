package com.hooney.lab.agent.ai.dto;

import jakarta.validation.constraints.NotBlank;

/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║         📨 RagRequest — RAG 질의 요청 DTO                         ║
 * ║                                                                  ║
 * ║  [용도] POST /api/v1/ai/rag 엔드포인트의 요청 바디 모델.            ║
 * ║  질문을 받아 벡터 DB에서 관련 문서를 검색한 후,                      ║
 * ║  검색된 문맥과 함께 LLM에게 답변을 생성하도록 요청합니다.             ║
 * ║                                                                  ║
 * ║  @author Hooney — AI FullStack Developer                         ║
 * ╚══════════════════════════════════════════════════════════════════╝
 *
 * @param question RAG 검색 및 LLM 답변 생성에 사용할 자연어 질문.
 *                 예: "Redis Sentinel 장애 복구 절차가 뭐야?"
 */
public record RagRequest(
        @NotBlank(message = "질문은 비어있을 수 없습니다.")
        String question
) {}
