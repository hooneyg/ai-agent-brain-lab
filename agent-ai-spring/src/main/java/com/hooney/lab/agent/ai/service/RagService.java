package com.hooney.lab.agent.ai.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.document.Document;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║         📚 RagService — Java-native RAG 파이프라인 서비스           ║
 * ║                                                                  ║
 * ║  [클래스 목적]                                                   ║
 * ║  Spring AI의 VectorStore와 ChatClient를 결합하여                   ║
 * ║  Java 단독으로 RAG(Retrieval-Augmented Generation)를 수행합니다.    ║
 * ║                                                                  ║
 * ║  [RAG 흐름]                                                     ║
 * ║  1. 질문을 벡터화하여 VectorStore에서 유사 문서 검색 (Retrieval)     ║
 * ║  2. 검색된 문서를 컨텍스트로 LLM에 전달 (Augmented)                 ║
 * ║  3. LLM이 컨텍스트 기반 답변 생성 (Generation)                     ║
 * ║                                                                  ║
 * ║  [Python agent-core와의 차이점]                                   ║
 * ║  - agent-core: ChromaDB + HuggingFace Embeddings (Python)        ║
 * ║  - 이 모듈: SimpleVectorStore + Ollama Embeddings (Java)          ║
 * ║  → 동일한 RAG 개념을 다른 기술 스택으로 구현하여 이중화 제공         ║
 * ║                                                                  ║
 * ║  @author Hooney — AI FullStack Developer                         ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */
@Service
public class RagService {

    private static final Logger log = LoggerFactory.getLogger(RagService.class);

    private final VectorStore vectorStore;
    private final ChatClient chatClient;

    /**
     * RAG 서비스 생성자.
     *
     * @param vectorStore       AiConfig에서 등록한 VectorStore 빈.
     * @param chatClientBuilder Spring AI가 자동 주입하는 ChatClient 빌더.
     */
    public RagService(VectorStore vectorStore, ChatClient.Builder chatClientBuilder) {
        this.vectorStore = vectorStore;
        this.chatClient = chatClientBuilder.build();
        log.info("✅ RagService initialized.");
    }

    /**
     * 문서를 벡터 저장소에 인덱싱합니다 (Ingestion).
     *
     * 실제 프로덕션에서는 파일 시스템에서 문서를 로드하겠지만,
     * 현재는 시연을 위해 샘플 문서를 하드코딩합니다.
     *
     * TODO: DocumentReader를 활용하여 외부 파일(.md, .pdf)에서
     *       동적으로 문서를 로드하도록 개선 필요.
     */
    public void ingestSampleDocuments() {
        log.info("📥 [RagService] Ingesting sample documents...");

        // 샘플 인프라 기술 문서 — 실제 환경에서는 파일 로더로 교체
        List<Document> documents = List.of(
                new Document("Kubernetes Pod가 CrashLoopBackOff 상태에 빠지면 "
                        + "컨테이너 로그를 확인하고, 리소스 제한(CPU/Memory limits)을 점검해야 합니다. "
                        + "OOMKilled인 경우 메모리 limit을 상향 조정하세요."),
                new Document("Redis Sentinel 장애 복구 절차: "
                        + "1) sentinel failover 명령으로 수동 페일오버를 시도합니다. "
                        + "2) 모든 sentinel 노드가 새 마스터를 인식하는지 확인합니다. "
                        + "3) 클라이언트 연결 설정의 sentinel 주소를 업데이트합니다."),
                new Document("Docker 컨테이너 네트워크 트러블슈팅: "
                        + "docker network inspect bridge로 네트워크 설정을 확인하고, "
                        + "iptables 규칙이 트래픽을 차단하고 있는지 점검합니다. "
                        + "DNS 해상도 문제가 있다면 /etc/resolv.conf를 확인하세요.")
        );

        vectorStore.add(documents);
        log.info("✅ [RagService] {} sample documents ingested.", documents.size());
    }

    /**
     * RAG 기반 질의/응답을 수행합니다.
     *
     * @param question 사용자의 자연어 질문.
     *                 예: "Pod가 CrashLoopBackOff 상태인데 어떻게 해결해?"
     * @return RAG 결과 Map:
     *         - "question": 원본 질문
     *         - "answer": LLM이 컨텍스트 기반으로 생성한 답변
     *         - "context": 검색된 참조 문서 목록
     */
    public Map<String, Object> queryWithContext(String question) {
        log.info("📚 [RagService] RAG query: {}", question);

        // 1단계: 벡터 유사도 검색 — 질문과 가장 관련 있는 상위 3개 문서 검색
        List<Document> relevantDocs = vectorStore.similaritySearch(
                SearchRequest.builder()
                        .query(question)
                        .topK(3)      // 상위 3개 문서 반환
                        .build()
        );

        // 검색된 문서들의 내용을 하나의 컨텍스트 문자열로 결합
        String context = relevantDocs.stream()
                .map(Document::getText)
                .collect(Collectors.joining("\n\n"));

        log.info("🔍 [RagService] Found {} relevant documents.", relevantDocs.size());

        // 2단계: LLM에 컨텍스트와 함께 질문 전달 (Augmented Generation)
        String ragPrompt = """
                다음 참고 문서를 기반으로 질문에 답변하세요.
                참고 문서에 없는 내용은 "참고 문서에서 확인할 수 없습니다"라고 명시하세요.
                
                [참고 문서]
                %s
                
                [질문]
                %s
                """.formatted(context, question);

        String answer = chatClient
                .prompt()
                .user(ragPrompt)
                .call()
                .content();

        log.info("✅ [RagService] RAG answer generated.");
        return Map.of(
                "question", question,
                "answer", answer,
                "context", relevantDocs.stream().map(Document::getText).toList()
        );
    }
}
