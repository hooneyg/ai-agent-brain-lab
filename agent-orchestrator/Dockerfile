# ╔══════════════════════════════════════════════════════════════════╗
# ║         ☕ Dockerfile — Agent Orchestrator (Spring Boot WebFlux)   ║
# ║                                                                  ║
# ║  [이미지 목적]                                                   ║
# ║  Python agent-core와 HTTP 통신하는 Java 기반 오케스트레이터.       ║
# ║  Spring WebFlux로 논블로킹 비동기 처리를 수행합니다.               ║
# ║                                                                  ║
# ║  [빌드 컨텍스트]                                                  ║
# ║  ⚠️ 이 Dockerfile은 프로젝트 루트에서 빌드해야 합니다.              ║
# ║  docker-compose.yml에서 build.context: . 로 설정됩니다.            ║
# ║  이유: Gradle Wrapper(gradlew)가 프로젝트 루트에만 존재하기 때문.    ║
# ║                                                                  ║
# ║  [멀티 스테이지 빌드]                                             ║
# ║  Stage 1 (builder): JDK + Gradle → bootJar 생성                  ║
# ║  Stage 2 (runtime): JRE 경량 이미지에서 JAR 실행                   ║
# ║  → 최종 이미지 크기를 약 70% 절감                                  ║
# ║                                                                  ║
# ║  @author Hooney — AI FullStack Developer                         ║
# ╚══════════════════════════════════════════════════════════════════╝

# ──────────────────────────────────────────────────────────────────
# Stage 1: 빌드 스테이지
# ──────────────────────────────────────────────────────────────────
FROM eclipse-temurin:21-jdk AS builder

WORKDIR /build

# 루트 프로젝트의 Gradle Wrapper와 설정 파일 복사
# ⚠️ 빌드 컨텍스트가 프로젝트 루트(.)이므로 상대경로로 접근 가능
COPY gradlew .
COPY gradle gradle
RUN chmod +x gradlew

# 루트 settings.gradle + 이 모듈의 build.gradle 복사
COPY settings.gradle .
COPY agent-orchestrator/build.gradle agent-orchestrator/build.gradle

# 의존성 사전 다운로드 (Docker 레이어 캐싱 활용)
# -p agent-orchestrator: 특정 모듈만 빌드
RUN ./gradlew :agent-orchestrator:dependencies --no-daemon || true

# 소스 코드 복사 후 빌드
COPY agent-orchestrator/src agent-orchestrator/src
RUN ./gradlew :agent-orchestrator:bootJar --no-daemon -x test

# ──────────────────────────────────────────────────────────────────
# Stage 2: 런타임 스테이지 — JRE 경량 이미지
# ──────────────────────────────────────────────────────────────────
FROM eclipse-temurin:21-jre

LABEL maintainer="Hooney <hooneyg@github.com>"
LABEL description="AI Agent Orchestrator — Java-Python Bridge"

# curl 설치 — Health Check에 사용
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 빌드 결과물(JAR) 복사
COPY --from=builder /build/agent-orchestrator/build/libs/*.jar app.jar

# 서비스 포트 노출 (기본: 8080)
EXPOSE 8080

# Health Check — 컨테이너 헬스 상태 자동 관리
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# JVM 컨테이너 최적화
# -XX:+UseContainerSupport: 컨테이너 CPU/메모리 제한을 JVM이 인식
# -XX:MaxRAMPercentage=75.0: 컨테이너 메모리의 75%를 힙에 할당
# -Dspring.profiles.active=docker: Docker 전용 프로파일 (호스트명 오버라이드)
ENTRYPOINT ["java", \
    "-XX:+UseContainerSupport", \
    "-XX:MaxRAMPercentage=75.0", \
    "-Dspring.profiles.active=docker", \
    "-jar", "app.jar"]
