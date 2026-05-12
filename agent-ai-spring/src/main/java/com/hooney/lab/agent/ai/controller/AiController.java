package com.hooney.lab.agent.ai.controller;

import com.hooney.lab.agent.ai.dto.*;
import com.hooney.lab.agent.ai.service.ChatService;
import com.hooney.lab.agent.ai.service.EmbeddingService;
import com.hooney.lab.agent.ai.service.RagService;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║         🎮 AiController — Spring AI REST API 컨트롤러             ║
 * ║                                                                  ║
 * ║  [클래스 목적]                                                   ║
 * ║  Java-native AI 기능(LLM Chat, Embedding, RAG)에 대한             ║
 * ║  REST API 엔드포인트를 제공합니다.                                  ║
 * ║                                                                  ║
 * ║  [API 목록]                                                     ║
 * ║  POST /api/v1/ai/chat       — LLM 질의/응답                      ║
 * ║  POST /api/v1/ai/embedding  — 텍스트 벡터화                       ║
 * ║  POST /api/v1/ai/rag        — RAG 기반 문서 검색 + 답변            ║
 * ║  POST /api/v1/ai/rag/ingest — RAG 지식 베이스 업데이트              ║
 * ║  GET  /api/v1/ai/health     — 서비스 상태 확인                     ║
 * ║                                                                  ║
 * ║  @author Hooney — AI FullStack Developer                         ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */
@RestController
@RequestMapping("/api/v1/ai")
public class AiController {

    private static final Logger log = LoggerFactory.getLogger(AiController.class);

    private final ChatService chatService;
    private final EmbeddingService embeddingService;
    private final RagService ragService;

    /**
     * 3개 서비스를 생성자 주입으로 받는다.
     * 생성자 주입은 필드 주입(@Autowired)보다 테스트 용이하고 불변성을 보장한다.
     */
    public AiController(ChatService chatService,
                         EmbeddingService embeddingService,
                         RagService ragService) {
        this.chatService = chatService;
        this.embeddingService = embeddingService;
        this.ragService = ragService;
    }

    /**
     * LLM 기반 자연어 질의/응답.
     *
     * @param request ChatRequest — { "message": "질문 내용" }
     * @return ChatResponse — { "answer": "...", "model": "...", "engine": "..." }
     */
    @PostMapping("/chat")
    public ResponseEntity<ChatResponse> chat(@Valid @RequestBody ChatRequest request) {
        log.info("💬 [POST /api/v1/ai/chat] message={}", request.message());
        String answer = chatService.chat(request.message());
        return ResponseEntity.ok(new ChatResponse(answer, "configured-model", "spring-ai"));
    }

    /**
     * 텍스트 벡터 임베딩 변환.
     *
     * @param request EmbeddingRequest — { "text": "벡터화할 텍스트" }
     * @return 벡터 정보 (차원, 미리보기 등)
     */
    @PostMapping("/embedding")
    public ResponseEntity<Map<String, Object>> embedding(@Valid @RequestBody EmbeddingRequest request) {
        log.info("🔢 [POST /api/v1/ai/embedding] text={}...", request.text().substring(0, Math.min(30, request.text().length())));
        return ResponseEntity.ok(embeddingService.embed(request.text()));
    }

    /**
     * RAG 기반 문서 검색 + LLM 답변 생성.
     *
     * @param request RagRequest — { "question": "검색할 질문" }
     * @return 답변 + 참조 문서 컨텍스트
     */
    @PostMapping("/rag")
    public ResponseEntity<Map<String, Object>> rag(@Valid @RequestBody RagRequest request) {
        log.info("📚 [POST /api/v1/ai/rag] question={}", request.question());
        return ResponseEntity.ok(ragService.queryWithContext(request.question()));
    }

    /**
     * RAG 지식 베이스 업데이트 (샘플 문서 인덱싱).
     *
     * @return 인덱싱 완료 확인 메시지
     */
    @PostMapping("/rag/ingest")
    public ResponseEntity<Map<String, String>> ingest() {
        log.info("📥 [POST /api/v1/ai/rag/ingest] Ingestion requested.");
        ragService.ingestSampleDocuments();
        return ResponseEntity.ok(Map.of("status", "completed", "message", "Sample documents ingested."));
    }

    /**
     * 서비스 상태 확인 (Health Check).
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of(
                "status", "UP",
                "service", "agent-ai-spring",
                "engine", "Spring AI + Ollama/HuggingFace"
        ));
    }
}
