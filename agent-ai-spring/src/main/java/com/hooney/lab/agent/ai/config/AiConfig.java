package com.hooney.lab.agent.ai.config;

import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.ai.vectorstore.SimpleVectorStore;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║         ⚙️ AiConfig — Spring AI 인프라 빈(Bean) 설정              ║
 * ║                                                                  ║
 * ║  [클래스 목적]                                                   ║
 * ║  Spring AI 프레임워크에서 사용하는 핵심 인프라 빈을 정의합니다.       ║
 * ║  VectorStore, ChatClient 등의 빈을 수동 등록하여                   ║
 * ║  자동 설정(Auto Configuration)을 보완합니다.                       ║
 * ║                                                                  ║
 * ║  [등록 빈 목록]                                                   ║
 * ║  - VectorStore: 벡터 유사도 검색을 위한 저장소 (RAG용)              ║
 * ║                                                                  ║
 * ║  [프로덕션 전환 가이드]                                           ║
 * ║  SimpleVectorStore는 개발/테스트 전용입니다.                       ║
 * ║  프로덕션에서는 아래 중 하나로 교체하세요:                           ║
 * ║  - pgvector (PostgreSQL 확장)                                     ║
 * ║  - Redis Vector Search                                            ║
 * ║  - ChromaDB                                                       ║
 * ║  - Pinecone / Weaviate (매니지드 서비스)                           ║
 * ║                                                                  ║
 * ║  @author Hooney — AI FullStack Developer                         ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */
@Configuration
public class AiConfig {

    /**
     * VectorStore 빈 등록.
     *
     * 인메모리 기반의 SimpleVectorStore를 사용합니다.
     * 별도 외부 DB 설치 없이 즉시 사용할 수 있어 개발/테스트에 적합합니다.
     * 서버 재시작 시 데이터가 유실되므로 프로덕션에서는 사용하지 마세요.
     *
     * @param embeddingModel Spring AI가 자동 주입하는 임베딩 모델.
     *                       application.yml의 ollama.embedding 또는
     *                       huggingface 설정에 따라 적절한 모델이 주입됩니다.
     * @return VectorStore 초기화된 벡터 저장소 인스턴스.
     */
    @Bean
    public VectorStore vectorStore(EmbeddingModel embeddingModel) {
        // SimpleVectorStore: JSON 파일 기반 벡터 저장소 (개발 전용)
        // EmbeddingModel: Ollama 또는 HuggingFace에서 자동 제공
        return SimpleVectorStore.builder(embeddingModel).build();
    }
}
