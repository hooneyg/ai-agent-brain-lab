package com.hooney.lab.agent;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║         🧠 AgentOrchestratorApplication (Main Entry)            ║
 * ║                                                                  ║
 * ║  [코드 역할]                                                     ║
 * ║  1. AI 에이전트 서비스 오케스트레이터 기동                          ║
 * ║  2. 비동기 추론 처리 및 외부 인터페이스 제어                        ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */
@SpringBootApplication
public class AgentOrchestratorApplication {

    public static void main(String[] args) {
        // AI 에이전트 브레인 오케스트레이터 서비스 시작
        SpringApplication.run(AgentOrchestratorApplication.class, args);
        System.out.println("🚀 AI Agent Orchestrator is Running on Port 8080");
    }
}
