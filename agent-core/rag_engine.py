# ╔══════════════════════════════════════════════════════════════════╗
# ║         🧠 rag_engine.py — RAG 지식 베이스 엔진                   ║
# ║                                                                  ║
# ║  [파일 목적]                                                     ║
# ║  Retrieval-Augmented Generation(RAG) 파이프라인을 구현합니다.       ║
# ║  인프라 기술 문서(.md)를 벡터 임베딩으로 변환하여 저장하고,          ║
# ║  사용자 질문에 관련된 문서 조각(chunk)을 검색하여 반환합니다.        ║
# ║                                                                  ║
# ║  [RAG 워크플로우]                                                 ║
# ║  1. Ingestion: 문서 로드 → 청크 분할 → 벡터 임베딩 → ChromaDB 저장 ║
# ║  2. Retrieval: 질문 임베딩 → 유사도 검색 → 상위 k개 문서 반환      ║
# ║                                                                  ║
# ║  [핵심 의존성]                                                   ║
# ║  - HuggingFace Embeddings: all-MiniLM-L6-v2 (로컬 실행)          ║
# ║  - ChromaDB: 벡터 저장소 (파일 기반 영속화)                        ║
# ║  - LangChain: 문서 로더 및 텍스트 분할기                           ║
# ║                                                                  ║
# ║  [작성자] Hooney — AI FullStack Developer                        ║
# ╚══════════════════════════════════════════════════════════════════╝

import os
import logging
from typing import List
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RAG-Engine")

load_dotenv()


class RagEngine:
    """
    RAG(Retrieval-Augmented Generation) 지식 베이스 엔진.

    인프라 기술 문서를 벡터화하여 저장하고,
    사용자 질문에 관련된 문서를 검색하여 LLM에게 '근거'를 제공합니다.
    이를 통해 LLM의 환각(Hallucination)을 억제하고 정확도를 높입니다.

    Attributes:
        docs_path (str): RAG 소스 문서가 있는 디렉토리 경로.
        persist_directory (str): ChromaDB 벡터 저장소의 영속화 경로.
        embeddings (HuggingFaceEmbeddings): 텍스트를 벡터로 변환하는 임베딩 모델.
        vector_db (Chroma | None): 벡터 저장소 인스턴스. ingest 후 초기화됨.
    """

    def __init__(self, docs_path: str, persist_directory: str = "./data/chromadb"):
        """
        RAG 엔진 초기화.

        Args:
            docs_path: 인프라 기술 문서(.md)가 있는 디렉토리 경로.
            persist_directory: ChromaDB 데이터가 저장될 로컬 경로.
                              서버 재시작 시에도 인덱싱 데이터를 유지한다.
        """
        self.docs_path = docs_path
        self.persist_directory = persist_directory

        # 로컬 임베딩 모델 초기화
        # all-MiniLM-L6-v2: 경량(80MB) + 빠른 속도 + 384차원 벡터 출력
        # 외부 API 호출 없이 로컬에서 실행되므로 비용이 발생하지 않는다.
        # 프로덕션에서는 nomic-embed-text(768차원) 또는 OpenAI embedding으로 교체 권장.
        try:
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            logger.info("✅ HuggingFaceEmbeddings initialized successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize embeddings: {str(e)}")
            raise

        # 벡터 DB는 ingest 실행 후 또는 기존 데이터 로드 시 초기화됨
        self.vector_db = None

    def ingest_docs(self):
        """
        지식 베이스 구축 (Ingestion).

        문서 처리 파이프라인:
        1. DirectoryLoader로 지정 경로의 모든 .md 파일을 로드
        2. RecursiveCharacterTextSplitter로 청크(chunk) 단위로 분할
        3. HuggingFace 임베딩 모델로 각 청크를 벡터화
        4. ChromaDB에 벡터와 원문을 함께 저장 (영속화)

        Note:
            - chunk_size=1000: 임베딩 모델의 최대 토큰(512)을 고려한 적정 크기.
              너무 크면 검색 정밀도가 떨어지고, 너무 작으면 맥락이 손실된다.
            - chunk_overlap=100: 청크 경계에서 문맥이 끊기는 것을 방지한다.
        """
        if not os.path.exists(self.docs_path):
            logger.error(f"❌ Source directory not found: {self.docs_path}")
            return

        try:
            logger.info(f"📂 Loading documents from: {self.docs_path}")
            # glob="**/*.md": 하위 디렉토리 포함 모든 마크다운 파일을 재귀적으로 로드
            loader = DirectoryLoader(
                self.docs_path,
                glob="**/*.md",
                loader_cls=UnstructuredMarkdownLoader
            )
            documents = loader.load()
            
            if not documents:
                logger.warning("⚠️ No documents found to ingest.")
                return

            # 청크 분할 — 긴 문서를 검색에 적합한 크기로 분할한다.
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,    # 각 청크의 최대 문자 수
                chunk_overlap=100   # 인접 청크 간 겹치는 문자 수 (문맥 보존)
            )
            chunks = text_splitter.split_documents(documents)
            
            logger.info(f"🧠 Embedding {len(chunks)} chunks...")
            # ChromaDB에 벡터 저장 — persist_directory로 파일 기반 영속화
            self.vector_db = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            logger.info("✅ Knowledge base built successfully!")
        except Exception as e:
            logger.error(f"❌ Ingestion failed: {str(e)}")

    def search_context(self, query: str, k: int = 3) -> str:
        """
        사용자 질문과 관련된 문서 컨텍스트를 검색합니다 (Retrieval).

        질문을 벡터로 변환한 후, ChromaDB에서 코사인 유사도 기반으로
        가장 관련성 높은 상위 k개 문서 청크를 검색하여 반환합니다.

        Args:
            query: 검색할 자연어 질문. 예: "Redis 캐시 장애 대응 방법"
            k: 반환할 상위 유사 문서 수 (기본값: 3).
               너무 많으면 LLM 입력 토큰이 초과되고, 너무 적으면 정보 부족.

        Returns:
            str: 검색된 문서들의 내용을 줄바꿈으로 연결한 문자열.
                 검색 실패 시 빈 문자열 반환.
        """
        try:
            if not self.vector_db:
                # 기존에 영속화된 ChromaDB 데이터가 있으면 로드한다.
                if os.path.exists(self.persist_directory):
                    self.vector_db = Chroma(
                        persist_directory=self.persist_directory,
                        embedding_function=self.embeddings
                    )
                else:
                    logger.warning("⚠️ Vector DB not found. Returning empty context.")
                    return ""
                
            # 코사인 유사도 기반 검색 — 질문과 의미적으로 가장 가까운 k개 문서 반환
            docs = self.vector_db.similarity_search(query, k=k)
            return "\n\n".join([doc.page_content for doc in docs])
        except Exception as e:
            logger.error(f"❌ Search failed: {str(e)}")
            return ""
