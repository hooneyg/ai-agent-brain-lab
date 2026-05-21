# -*- coding: utf-8 -*-
"""
🧠 test_react_flow.py — ReAct 에이전트 추론 흐름 단위/통합 테스트 (최종 개선버전)

이 테스트 코드는 ReAct 에이전트(AgentBrain)의 자율 추론 엔진이
Thought -> Action -> Observation -> Final Answer로 이어지는 단계적 흐름을
일관되게 처리하는지 검증합니다. ChatOpenAI 대신 FakeChatModel을 사용하여
실제 API 호출을 차단하고 Pydantic validation 및 속성 삭제 제한 에러를 우회합니다.

작성자: Hooney — AI FullStack Developer
"""

import os
from typing import Any, List, Optional
import pytest
from unittest.mock import MagicMock, patch

# 테스트 실행 시 실제 API 호출이 차단되도록 가짜 환경 변수를 선언합니다.
os.environ["OPENROUTER_API_KEY"] = "fake-api-key"
os.environ["OPENROUTER_BASE_URL"] = "https://openrouter.ai/api/v1"
os.environ["OPENROUTER_MODEL"] = "openai/gpt-4o"

from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration
from agent_brain import AgentBrain
from rag_engine import RagEngine


class FakeChatModel(BaseChatModel):
    """테스트용 가짜 ChatModel 클래스"""
    responses: List[BaseMessage]
    i: int = 0

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        response = self.responses[self.i]
        self.i += 1
        return ChatResult(generations=[ChatGeneration(message=response)])

    @property
    def _llm_type(self) -> str:
        return "fake-chat-model"


@pytest.fixture
def mock_rag():
    """RAG 엔진 모킹 피스처"""
    mock_instance = MagicMock(spec=RagEngine)
    mock_instance.search_context.return_value = "Mocked system document context: Redis configuration details."
    return mock_instance


def test_agent_brain_initialization(mock_rag):
    """
    AgentBrain 초기화가 정상적으로 완료되고,
    ReAct 실행을 위한 툴과 프롬프트가 올바르게 셋업되는지 검증합니다.
    """
    agent = AgentBrain(rag_engine=mock_rag)
    
    assert agent.rag == mock_rag
    assert agent.agent_executor is not None
    # 등록된 도구가 2개(get_infra_status, generate_fix_script)인지 확인
    assert len(agent.agent_executor.tools) == 2
    tool_names = [t.name for t in agent.agent_executor.tools]
    assert "get_infra_status" in tool_names
    assert "generate_fix_script" in tool_names


def test_agent_tools_execution():
    """
    Agent가 사용하는 커스텀 도구들(get_infra_status, generate_fix_script)이
    입력 인자에 따라 예상되는 정적 시뮬레이션 결과를 올바르게 반환하는지 검증합니다.
    """
    # 1. get_infra_status 도구 검증
    status_result = AgentBrain.get_infra_status.run("payment-service-01")
    assert "payment-service-01" in status_result
    assert "DEGRADED" in status_result

    # 2. generate_fix_script 도구 검증
    script_result = AgentBrain.generate_fix_script.run("high CPU load")
    assert "Fix high CPU load" in script_result
    assert "systemd: name=business-service state=restarted" in script_result


def test_agent_react_execution_flow(mock_rag):
    """
    LLM의 ReAct 출력 패턴을 단계적으로 Mocking하여,
    Thought -> Action (get_infra_status 실행) -> Observation -> Thought -> Final Answer
    로 이어지는 전체 추론 흐름이 중간 파싱 에러 없이 올바르게 완료되는지 검증합니다.
    """
    # 2. ReAct 추론 단계를 위한 모킹 메시지 정의
    # 첫 번째 답변: 도구 호출 요구 (ReAct 포맷)
    first_llm_response = AIMessage(
        content="Thought: 결제 서비스의 인프라 상태를 확인해야 합니다. get_infra_status 도구를 사용하겠습니다.\n"
                "Action: get_infra_status\n"
                "Action Input: payment-service-01"
    )
    # 두 번째 답변: 도구 실행 결과(Observation)를 확인한 후, 최종 답변 도출 (ReAct 포맷)
    second_llm_response = AIMessage(
        content="Thought: 결제 서비스 노드가 CPU 과부하로 인해 DEGRADED 상태임을 확인했습니다. 조치가 필요합니다.\n"
                "Final Answer: 결제 서비스 노드(payment-service-01)는 현재 CPU 부하가 높아서 성능 저하(DEGRADED) 상태에 처해 있습니다."
    )
    
    # Fake LLM 인스턴스 생성
    fake_llm = FakeChatModel(responses=[first_llm_response, second_llm_response])

    # ChatOpenAI 생성을 패치하여 가짜 LLM을 주입함으로써 Pydantic 및 API 키 오류를 우회합니다.
    with patch("agent_brain.ChatOpenAI", return_value=fake_llm):
        # 1. AgentBrain 인스턴스를 정상 생성합니다.
        agent = AgentBrain(rag_engine=mock_rag)
        
        query = "결제 서비스에 문제가 있어. 상태가 어떤지 확인해줘."
        result = agent.run(query)
        
        # RAG 엔진이 질문에 관련된 문서를 정상 탐색하였는지 검증
        mock_rag.search_context.assert_called_once_with(query)
        
        # 에이전트의 최종 출력이 모킹된 Final Answer와 일치하는지 검증
        assert "payment-service-01" in result["output"]
        assert "성능 저하(DEGRADED)" in result["output"]
        
        # 가짜 LLM이 2회 정상적으로 호출되었는지 확인
        assert fake_llm.i == 2
