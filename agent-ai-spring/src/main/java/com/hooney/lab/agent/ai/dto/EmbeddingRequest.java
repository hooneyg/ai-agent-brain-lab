package com.hooney.lab.agent.ai.dto;

import jakarta.validation.constraints.NotBlank;

/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║         📨 EmbeddingRequest — 텍스트 임베딩 요청 DTO               ║
 * ║                                                                  ║
 * ║  [용도] POST /api/v1/ai/embedding 엔드포인트의 요청 바디 모델.      ║
 * ║  텍스트를 벡터 표현(float 배열)으로 변환하기 위해 사용합니다.         ║
 * ║                                                                  ║
 * ║  @author Hooney — AI FullStack Developer                         ║
 * ╚══════════════════════════════════════════════════════════════════╝
 *
 * @param text 벡터화할 텍스트. 빈 문자열 불가.
 *             예: "Kubernetes Pod CrashLoopBackOff 원인 분석"
 */
public record EmbeddingRequest(
        @NotBlank(message = "임베딩할 텍스트는 비어있을 수 없습니다.")
        String text
) {}
