# ╔══════════════════════════════════════════════════════════════════╗
# ║         🧠 agent_brain.py — 자율 추론 에이전트 코어               ║
# ║                                                                  ║
# ║  [파일 목적]                                                     ║
# ║  ReAct(Reason + Act) 패턴 기반의 자율 추론 에이전트를 구현합니다.   ║
# ║  LLM이 스스로 생각(Thought)하고, 도구를 사용(Action)하며,          ║
# ║  결과를 관찰(Observation)하여 최종 답변을 도출하는 워크플로우입니다.  ║
# ║                                                                  ║
# ║  [핵심 의존성]                                                   ║
# ║  - LangChain: 에이전트 프레임워크 (create_react_agent)            ║
# ║  - ChatOpenAI: OpenRouter를 통한 LLM 호출 (GPT-4o, Claude 등)    ║
# ║  - RagEngine: 인프라 기술 문서 기반 컨텍스트 검색                   ║
# ║                                                                  ║
# ║  [작성자] Hooney — AI FullStack Developer                        ║
# ╚══════════════════════════════════════════════════════════════════╝

import os
from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain_classic.prompts import PromptTemplate
from langchain_classic.tools import tool
from rag_engine import RagEngine

# .env 파일에서 환경 변수를 로드한다.
# API Key, LLM 모델명, Base URL 등의 민감 정보는 환경 변수로 관리한다.
load_dotenv()

import logging

# 모듈 전용 로거 생성
# "Agent-Brain" 네임스페이스로 로그를 분리하여 다른 모듈 로그와 구분한다.
logger = logging.getLogger("Agent-Brain")


class AgentBrain:
    """
    자율 추론 에이전트 (Autonomous Reasoning Agent).

    ReAct 패턴을 기반으로 동작하며, 다음 3단계를 반복 수행합니다:
    1. Thought  — LLM이 현재 상황을 분석하고 다음 행동을 계획
    2. Action   — 적절한 도구(Tool)를 선택하여 실행
    3. Observation — 도구 실행 결과를 관찰하고 다음 단계 결정

    Attributes:
        llm (ChatOpenAI): OpenRouter를 통해 연결된 LLM 인스턴스.
        rag (RagEngine): 인프라 기술 문서 검색을 위한 RAG 엔진.
        agent_executor (AgentExecutor): ReAct 에이전트 실행기.
    """

    def __init__(self, rag_engine: RagEngine):
        """
        에이전트 브레인 초기화.

        Args:
            rag_engine (RagEngine): 사전 초기화된 RAG 엔진 인스턴스.
                                   인프라 기술 문서에서 관련 컨텍스트를 검색하는 데 사용.

        Raises:
            Exception: LLM 초기화 실패 시 (API Key 누락, 네트워크 오류 등).

        Note:
            OpenRouter를 LLM 게이트웨이로 사용합니다.
            base_url 끝에 슬래시(/)가 중복되면 API 호출이 실패하므로 rstrip으로 제거합니다.
            API Key가 없는 경우 Ollama 로컬 모델을 대안으로 사용할 수 있습니다.
            (.env에서 OPENROUTER_BASE_URL=http://localhost:11434/v1 로 변경)
        """
        try:
            # OpenRouter base URL에서 후행 슬래시를 제거한다.
            # 예: "https://openrouter.ai/api/v1/" → "https://openrouter.ai/api/v1"
            # 후행 슬래시가 있으면 LLM API 호출 시 404 에러가 발생할 수 있다.
            base_url = os.getenv("OPENROUTER_BASE_URL")
            if base_url:
                base_url = base_url.rstrip("/")

            self.llm = ChatOpenAI(
                # 사용할 LLM 모델명 (기본값: openai/gpt-4o)
                # OpenRouter는 "제공사/모델명" 형식을 사용한다.
                # 예: "openai/gpt-4o", "anthropic/claude-3.5-sonnet", "meta-llama/llama-3.1-8b"
                model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o"),

                # API 인증 키
                # [OPENROUTER_API_KEY] — https://openrouter.ai/keys 에서 발급
                # Ollama 로컬 사용 시: 아무 문자열 입력 (예: "ollama")
                openai_api_key=os.getenv("OPENROUTER_API_KEY"),

                # API 엔드포인트 URL
                base_url=base_url,

                # temperature=0: 결정적(deterministic) 응답을 보장한다.
                # 인프라 진단에는 창의적 응답보다 정확한 응답이 중요하므로 0으로 설정한다.
                temperature=0,

                # OpenRouter 필수 헤더
                # HTTP-Referer: 요청 출처 식별 (OpenRouter 정책 요구사항)
                # X-Title: 대시보드에서 프로젝트를 식별하기 위한 명칭
                default_headers={
                    "HTTP-Referer": "https://github.com/hooneyg/ai-agent-brain-lab",
                    "X-Title": "AI Agent Brain Lab",
                }
            )
            logger.info(f"✅ LLM initialized with model: {os.getenv('OPENROUTER_MODEL', 'openai/gpt-4o')}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {str(e)}")
            raise

        # RAG 엔진 주입 — 에이전트가 답변 전에 관련 기술 문서를 검색하여 환각을 방지한다.
        self.rag = rag_engine

        # ReAct 에이전트 설정 및 실행기 생성
        self.agent_executor = self._setup_agent()

    @staticmethod
    @tool
    def get_infra_status(node_name: str) -> str:
        """
        지정한 인프라 노드의 현재 상태를 조회합니다.

        이 도구는 ReAct 에이전트가 인프라 상태를 확인할 때 자동으로 호출됩니다.
        실제 프로덕션에서는 Prometheus/Grafana API 또는 Kubernetes API와 연동합니다.

        Args:
            node_name (str): 조회할 인프라 노드의 이름.
                            예: "payment-service-01", "redis-cluster-primary"

        Returns:
            str: 해당 노드의 현재 상태 정보 문자열.
        """
        logger.info(f"🔍 [Tool] Getting infra status for: {node_name}")
        # TODO: 실제 인프라 모니터링 API(Prometheus, K8S API)와 연동 필요
        # 현재는 시연을 위한 시뮬레이션 응답을 반환한다.
        return f"Node '{node_name}' is currently in 'DEGRADED' state due to high CPU load."

    @staticmethod
    @tool
    def generate_fix_script(issue_desc: str) -> str:
        """
        인프라 문제를 해결하기 위한 Ansible 또는 K8S 스크립트를 생성합니다.

        에이전트가 장애 원인을 파악한 후, 복구를 위한 자동화 스크립트를 생성할 때 사용됩니다.
        실제 프로덕션에서는 사전 검증된 Playbook 템플릿 라이브러리에서 매칭합니다.

        Args:
            issue_desc (str): 해결해야 할 인프라 이슈에 대한 설명.
                             예: "high CPU load on payment service"

        Returns:
            str: 해당 이슈를 해결하기 위한 Ansible Playbook YAML 스크립트.

        Note:
            ⚠️ Human-in-the-loop: 생성된 스크립트는 반드시 관리자가 검토한 후 실행해야 합니다.
            에이전트가 자동으로 인프라를 변경하는 것은 위험하므로 실행 권한은 제한됩니다.
        """
        logger.info(f"🛠️ [Tool] Generating fix script for: {issue_desc}")
        # TODO: 실제 Ansible Playbook 템플릿 라이브러리와 연동
        return f"--- \n- name: Fix {issue_desc}\n  hosts: all\n  tasks:\n    - name: Restart service\n      systemd: name=business-service state=restarted"

    def _setup_agent(self):
        """
        ReAct 에이전트를 구성하고 실행기(Executor)를 반환합니다.

        이 메서드는 다음 3가지를 설정합니다:
        1. 도구(Tools) 목록 — 에이전트가 사용할 수 있는 외부 도구들
        2. 프롬프트 템플릿 — ReAct 패턴의 Thought/Action/Observation 형식을 강제하는 지시문
        3. 에이전트 실행기 — 위 요소들을 결합하여 추론 루프를 관리하는 엔진

        Returns:
            AgentExecutor: 구성이 완료된 ReAct 에이전트 실행기.
        """
        # 1. 에이전트가 사용할 도구 목록을 정의한다.
        # 각 도구는 @tool 데코레이터가 붙은 함수로, 이름과 설명이 자동으로 LLM에 전달된다.
        tools = [self.get_infra_status, self.generate_fix_script]
        
        # 2. ReAct 프롬프트 템플릿을 작성한다.
        # 이 템플릿은 LLM이 반드시 Thought → Action → Observation 형식을 따르도록 강제한다.
        # {tools}: 사용 가능한 도구 목록과 설명이 자동 삽입된다.
        # {tool_names}: 도구 이름만 쉼표로 구분하여 삽입된다.
        # {input}: 사용자의 원래 질문이 삽입된다.
        # {agent_scratchpad}: 이전 Thought/Action/Observation 이력이 누적 삽입된다.
        template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)
        
        # 3. ReAct 에이전트를 생성하고 실행기로 감싼다.
        agent = create_react_agent(self.llm, tools, prompt)

        # handle_parsing_errors=True: LLM이 형식을 어기면 에러 메시지를 LLM에게 피드백하여
        # 스스로 형식을 수정하도록 유도한다. (트러블슈팅 가이드 #2 참조)
        return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    def run(self, user_query: str):
        """
        사용자 질문에 대해 RAG + ReAct 추론을 수행하고 최종 답변을 반환합니다.

        실행 흐름:
        1. RAG 엔진에서 질문과 관련된 기술 문서 컨텍스트를 검색
        2. 검색된 컨텍스트를 질문에 첨부하여 LLM의 환각(Hallucination)을 방지
        3. ReAct 에이전트가 Thought → Action → Observation 루프를 수행
        4. 최종 답변(Final Answer)을 반환

        Args:
            user_query (str): 사용자가 입력한 자연어 질문.
                             예: "결제 서비스 노드의 장애 원인을 분석해줘"

        Returns:
            dict: 에이전트 실행 결과. 'output' 키에 최종 답변이 포함됨.
                  실패 시 에러 메시지가 포함된 dict를 반환.
        """
        try:
            logger.info(f"🚀 Running agent with query: {user_query}")
            
            # [핵심] RAG를 통해 관련 지식을 먼저 확보한다.
            # 이 컨텍스트가 LLM에게 "근거"를 제공하여 환각(hallucination)을 억제한다.
            # 예: 사용자가 "Redis 장애"를 물으면, infra-master-lab의 Redis 관련 문서가 검색된다.
            context = self.rag.search_context(user_query)

            # RAG 컨텍스트를 질문 앞에 첨부한다.
            # 에이전트는 이 컨텍스트를 참조하여 근거 있는 답변을 생성한다.
            enriched_query = f"Context: {context}\n\nQuestion: {user_query}"
            
            # ReAct 에이전트 실행 — Thought/Action/Observation 루프가 자동으로 진행된다.
            response = self.agent_executor.invoke({"input": enriched_query})
            logger.info("✅ Agent execution completed successfully.")
            return response
        except Exception as e:
            logger.error(f"❌ Agent execution failed: {str(e)}")
            return {"output": f"에이전트 실행 중 오류가 발생했습니다: {str(e)}"}
