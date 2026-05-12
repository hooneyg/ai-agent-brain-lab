#!/bin/bash

# ╔══════════════════════════════════════════════════════════════════╗
# ║         🚀 curl-agent-query.sh — AI Agent API 테스트 스크립트      ║
# ║                                                                  ║
# ║  [스크립트 목적]                                                   ║
# ║  터미널(CLI) 환경에서 Agent Core의 REST API(/ask)를 테스트합니다.    ║
# ║  간단한 bash 명령어(curl)와 jq를 활용하여 JSON 응답을 예쁘게 출력합니다.║
# ║                                                                  ║
# ║  [사용 방법]                                                       ║
# ║  1. 인자 없이 실행 (기본 질문 사용):                                ║
# ║     ./curl-agent-query.sh                                         ║
# ║  2. 커스텀 질문으로 실행:                                          ║
# ║     ./curl-agent-query.sh "우리 시스템의 장애 복구 매뉴얼을 알려줘" ║
# ╚══════════════════════════════════════════════════════════════════╝

# AI Agent Core가 동작 중인 로컬 엔드포인트 URL
AGENT_URL="http://localhost:8000/ask"

# 사용자가 입력한 파라미터($1)가 있으면 해당 값을 사용하고, 없으면 기본 영문 질문을 사용합니다.
# (기본 질문: "새로운 마이크로서비스를 배포하기 위한 표준 절차가 무엇인가요?")
QUERY=${1:-"새로운 마이크로서비스를 배포하기 위한 표준 절차가 무엇인가요?"}

echo "🤖 AI Agent Brain에게 질문을 전송합니다: $QUERY"

# curl을 사용하여 POST 요청 전송
# -H: JSON 데이터 형식임을 명시
# -d: 질문 내용이 담긴 JSON 페이로드 전송
# | jq .: 반환된 JSON 응답을 가독성 있게 포맷팅하여 출력
curl -X POST "$AGENT_URL" \
     -H "Content-Type: application/json" \
     -d "{\"query\": \"$QUERY\"}" \
     | jq .
