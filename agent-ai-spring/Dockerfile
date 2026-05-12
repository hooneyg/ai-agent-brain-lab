# ╔══════════════════════════════════════════════════════════════════╗
# ║         🤖 Dockerfile — Spring AI + HuggingFace 모듈              ║
# ║                                                                  ║
# ║  [이미지 목적]                                                   ║
# ║  Java-native AI 서비스 — LLM Chat, Embedding, RAG REST API.       ║
# ║  Spring AI + Ollama/HuggingFace 기반으로 포트 8081에서 서비스됩니다. ║
# ║                                                                  ║
# ║  [빌드 컨텍스트]                                                  ║
# ║  ⚠️ 이 Dockerfile은 프로젝트 루트에서 빌드해야 합니다.              ║
# ║  docker-compose.yml에서 build.context: . 로 설정됩니다.            ║
# ║  이유: Gradle Wrapper(gradlew)가 프로젝트 루트에만 존재하기 때문.    ║
# ║                                                                  ║
# ║  [멀티 스테이지 빌드]                                             ║
# ║  Stage 1 (builder): JDK + Gradle → bootJar 생성                  ║
# ║  Stage 2 (runtime): JRE 경량 이미지에서 JAR 실행                   ║
# ║                                                                  ║
# ║  @author Hooney — AI FullStack Developer                         ║
# ╚══════════════════════════════════════════════════════════════════╝

# ──────────────────────────────────────────────────────────────────
# Stage 1: 빌드 스테이지
# ──────────────────────────────────────────────────────────────────
FROM eclipse-temurin:21-jdk AS builder

WORKDIR /build

# 루트 프로젝트의 Gradle Wrapper와 설정 파일 복사
COPY gradlew .
COPY gradle gradle
RUN chmod +x gradlew

# 루트 settings.gradle + 이 모듈의 build.gradle 복사
COPY settings.gradle .
COPY agent-ai-spring/build.gradle agent-ai-spring/build.gradle

# 의존성 사전 다운로드 (Docker 레이어 캐싱 활용)
RUN ./gradlew :agent-ai-spring:dependencies --no-daemon || true

# 소스 코드 복사 후 빌드
COPY agent-ai-spring/src agent-ai-spring/src
RUN ./gradlew :agent-ai-spring:bootJar --no-daemon -x test

# ──────────────────────────────────────────────────────────────────
# Stage 2: 런타임 스테이지 — JRE 경량 이미지
# ──────────────────────────────────────────────────────────────────
FROM eclipse-temurin:21-jre

LABEL maintainer="Hooney <hooneyg@github.com>"
LABEL description="Spring AI Module — Java-native LLM/RAG Service"

# curl 설치 — Health Check에 사용
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 빌드 결과물(JAR) 복사
COPY --from=builder /build/agent-ai-spring/build/libs/*.jar app.jar

# 서비스 포트 노출 (8081)
EXPOSE 8081

# Health Check — /api/v1/ai/health 엔드포인트
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8081/api/v1/ai/health || exit 1

# JVM 컨테이너 최적화 + Docker 프로파일 활성화
ENTRYPOINT ["java", \
    "-XX:+UseContainerSupport", \
    "-XX:MaxRAMPercentage=75.0", \
    "-Dspring.profiles.active=docker", \
    "-jar", "app.jar"]
