# ╔══════════════════════════════════════════════════════════════════╗
# ║         🧠 agent_brain.py (Autonomous Reasoning Core)           ║
# ║                                                                  ║
# ║  [에이전트 역할]                                                 ║
# ║  1. ReAct 패턴을 이용한 복합 문제 추론 및 계획 수립                ║
# ║  2. 외부 도구(Tools)를 사용하여 인프라 제어 및 분석 수행           ║
# ╚══════════════════════════════════════════════════════════════════╝

import os
from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain_classic.prompts import PromptTemplate
from langchain_classic.tools import tool
from rag_engine import RagEngine

# 환경 변수 로드
load_dotenv()

import logging

# 로깅 설정
logger = logging.getLogger("Agent-Brain")

class AgentBrain:
    def __init__(self, rag_engine: RagEngine):
        # OpenRouter 설정 적용 (rstrip으로 중복 슬래시 방지)
        try:
            base_url = os.getenv("OPENROUTER_BASE_URL")
            if base_url:
                base_url = base_url.rstrip("/")

            self.llm = ChatOpenAI(
                model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o"),
                openai_api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url=base_url,
                temperature=0,
                default_headers={
                    "HTTP-Referer": "https://github.com/hooneyg/ai-agent-brain-lab",
                    "X-Title": "AI Agent Brain Lab",
                }
            )
            logger.info(f"✅ LLM initialized with model: {os.getenv('OPENROUTER_MODEL', 'openai/gpt-4o')}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {str(e)}")
            raise

        self.rag = rag_engine
        self.agent_executor = self._setup_agent()

    @staticmethod
    @tool
    def get_infra_status(node_name: str) -> str:
        """지정한 인프라 노드의 현재 상태를 조회합니다."""
        logger.info(f"🔍 [Tool] Getting infra status for: {node_name}")
        return f"Node '{node_name}' is currently in 'DEGRADED' state due to high CPU load."

    @staticmethod
    @tool
    def generate_fix_script(issue_desc: str) -> str:
        """인프라 문제를 해결하기 위한 Ansible 또는 K8S 스크립트를 생성합니다."""
        logger.info(f"🛠️ [Tool] Generating fix script for: {issue_desc}")
        return f"--- \n- name: Fix {issue_desc}\n  hosts: all\n  tasks:\n    - name: Restart service\n      systemd: name=business-service state=restarted"

    def _setup_agent(self):
        # 1. 사용할 도구 목록 정의
        tools = [self.get_infra_status, self.generate_fix_script]
        
        # 2. ReAct 프롬프트 템플릿 작성
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
        
        # 3. ReAct 에이전트 생성
        agent = create_react_agent(self.llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    def run(self, user_query: str):
        """사용자 질문에 대해 추론을 수행하고 최종 답변을 반환합니다."""
        try:
            logger.info(f"🚀 Running agent with query: {user_query}")
            
            # RAG를 통해 관련 지식 먼저 확보
            context = self.rag.search_context(user_query)
            enriched_query = f"Context: {context}\n\nQuestion: {user_query}"
            
            response = self.agent_executor.invoke({"input": enriched_query})
            logger.info("✅ Agent execution completed successfully.")
            return response
        except Exception as e:
            logger.error(f"❌ Agent execution failed: {str(e)}")
            return {"output": f"에이전트 실행 중 오류가 발생했습니다: {str(e)}"}
