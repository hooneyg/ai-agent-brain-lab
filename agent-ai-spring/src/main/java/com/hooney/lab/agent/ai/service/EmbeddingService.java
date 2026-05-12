package com.hooney.lab.agent.ai.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.ai.embedding.EmbeddingResponse;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║         🔢 EmbeddingService — 텍스트 벡터 임베딩 서비스             ║
 * ║                                                                  ║
 * ║  [클래스 목적]                                                   ║
 * ║  텍스트를 고차원 벡터(float[])로 변환하는 임베딩 서비스입니다.        ║
 * ║  변환된 벡터는 RAG 파이프라인의 유사도 검색에 사용됩니다.             ║
 * ║                                                                  ║
 * ║  [사용 모델]                                                     ║
 * ║  application.yml 설정에 따라 자동 결정됩니다:                       ║
 * ║  - Ollama: nomic-embed-text (768차원, 무료)                       ║
 * ║  - HuggingFace: sentence-transformers 모델                       ║
 * ║  - OpenAI: text-embedding-3-small (1536차원, 유료)                ║
 * ║                                                                  ║
 * ║  @author Hooney — AI FullStack Developer                         ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */
@Service
public class EmbeddingService {

    private static final Logger log = LoggerFactory.getLogger(EmbeddingService.class);

    /** Spring AI EmbeddingModel — 텍스트→벡터 변환을 추상화 */
    private final EmbeddingModel embeddingModel;

    /**
     * @param embeddingModel Spring AI가 자동 주입하는 임베딩 모델.
     *                       Ollama 또는 HuggingFace 설정에 따라 주입됨.
     */
    public EmbeddingService(EmbeddingModel embeddingModel) {
        this.embeddingModel = embeddingModel;
        log.info("✅ EmbeddingService initialized.");
    }

    /**
     * 텍스트를 벡터 임베딩으로 변환합니다.
     *
     * @param text 벡터화할 텍스트. 예: "Kubernetes Pod 재시작 원인 분석"
     * @return 변환 결과 Map:
     *         - "text": 원본 텍스트
     *         - "dimension": 벡터 차원 수 (예: 768)
     *         - "embedding": float[] 벡터 값 (처음 5개만 미리보기)
     */
    public Map<String, Object> embed(String text) {
        log.info("🔢 [EmbeddingService] Embedding text: {}...", text.substring(0, Math.min(50, text.length())));
        try {
            EmbeddingResponse response = embeddingModel.embedForResponse(List.of(text));
            float[] embedding = response.getResult().getOutput();

            log.info("✅ [EmbeddingService] Embedding generated. Dimension: {}", embedding.length);
            return Map.of(
                    "text", text,
                    "dimension", embedding.length,
                    // 전체 벡터 대신 처음 5개만 반환 (API 응답 크기 최적화)
                    "embedding_preview", truncate(embedding, 5)
            );
        } catch (Exception e) {
            log.error("❌ [EmbeddingService] Embedding failed: {}", e.getMessage());
            throw new RuntimeException("임베딩 변환에 실패했습니다: " + e.getMessage(), e);
        }
    }

    /**
     * float 배열의 처음 n개 요소만 추출합니다 (응답 크기 최적화).
     */
    private float[] truncate(float[] arr, int n) {
        float[] result = new float[Math.min(n, arr.length)];
        System.arraycopy(arr, 0, result, 0, result.length);
        return result;
    }
}
