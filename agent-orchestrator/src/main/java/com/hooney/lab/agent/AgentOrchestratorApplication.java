package com.hooney.lab.agent;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║         🧠 AgentOrchestratorApplication — 오케스트레이터 메인      ║
 * ║                                                                  ║
 * ║  [클래스 목적]                                                   ║
 * ║  AI 에이전트 서비스의 오케스트레이션 계층 진입점입니다.               ║
 * ║  이 모듈은 Python 기반 AI Agent Core(FastAPI)와 HTTP 통신하여       ║
 * ║  사용자의 질의를 전달하고 추론 결과를 받아 가공합니다.                 ║
 * ║                                                                  ║
 * ║  [아키텍처 위치]                                                  ║
 * ║  Client → agent-orchestrator(이 모듈) → agent-core(Python)        ║
 * ║                                                                  ║
 * ║  [설계 근거]                                                     ║
 * ║  Java/Spring Boot는 엔터프라이즈 백엔드 표준이므로 API 게이트웨이,   ║
 * ║  인증, 모니터링, 재시도(Retry) 정책을 관리하기에 적합합니다.          ║
 * ║  AI 추론은 Python 생태계(LangChain, HuggingFace)가 우수하므로       ║
 * ║  HTTP 기반으로 두 언어의 장점을 결합하는 폴리글랏 아키텍처를          ║
 * ║  채택했습니다. (ADR-001 참조)                                      ║
 * ║                                                                  ║
 * ║  [기술 스택]                                                     ║
 * ║  - Spring Boot 4.0.6 + WebFlux (논블로킹 비동기 HTTP)              ║
 * ║  - Java 21 (LTS)                                                  ║
 * ║                                                                  ║
 * ║  @author Hooney — AI FullStack Developer                         ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */
@SpringBootApplication
public class AgentOrchestratorApplication {

    /**
     * 애플리케이션 진입점.
     *
     * Spring Boot 자동 설정(Auto Configuration)이 적용되어
     * WebFlux, Jackson, Validation 등의 인프라가 자동 구성됩니다.
     *
     * @param args 커맨드 라인 인자 (프로파일 지정 등에 사용)
     *             예: --spring.profiles.active=docker
     */
    public static void main(String[] args) {
        // AI 에이전트 오케스트레이터 서비스 시작
        // 기본 포트: 8080 (application.yml에서 변경 가능)
        SpringApplication.run(AgentOrchestratorApplication.class, args);
        System.out.println("🚀 AI Agent Orchestrator is Running on Port 8080");
    }
}
