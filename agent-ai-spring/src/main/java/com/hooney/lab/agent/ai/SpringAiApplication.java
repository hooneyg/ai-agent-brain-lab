package com.hooney.lab.agent.ai;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║         🤖 SpringAiApplication — Java-native AI 서비스 진입점     ║
 * ║                                                                  ║
 * ║  [모듈 목적]                                                     ║
 * ║  Spring AI + HuggingFace를 활용하여 Python 없이 Java만으로          ║
 * ║  LLM Chat, Embedding, RAG를 수행하는 독립 마이크로서비스입니다.      ║
 * ║                                                                  ║
 * ║  [제공 REST API]                                                  ║
 * ║  POST /api/v1/ai/chat       — LLM 기반 자연어 질의/응답            ║
 * ║  POST /api/v1/ai/embedding  — 텍스트 벡터 임베딩 변환               ║
 * ║  POST /api/v1/ai/rag        — RAG 기반 문서 검색 + LLM 답변        ║
 * ║                                                                  ║
 * ║  [설계 근거 — ADR-002 참조]                                       ║
 * ║  Python agent-core가 이미 LangChain 기반 ReAct를 제공하지만,        ║
 * ║  순수 Java 환경에서도 AI 기능을 사용할 수 있도록 이중 엔진을 제공.    ║
 * ║  이를 통해 Python 서버 장애 시에도 기본적인 AI 질의/응답 가능.       ║
 * ║                                                                  ║
 * ║  [포트] 8081 (application.yml에서 설정)                            ║
 * ║                                                                  ║
 * ║  @author Hooney — AI FullStack Developer                         ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */
@SpringBootApplication
public class SpringAiApplication {

    /**
     * Spring AI 모듈 진입점.
     *
     * @param args 커맨드 라인 인자 (프로파일 지정 등)
     *             예: --spring.profiles.active=ollama (로컬 모델 사용)
     */
    public static void main(String[] args) {
        SpringApplication.run(SpringAiApplication.class, args);
        System.out.println("🤖 Spring AI Module is Running on Port 8081");
    }
}
