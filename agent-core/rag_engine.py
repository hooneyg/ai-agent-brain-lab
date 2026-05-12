# ╔══════════════════════════════════════════════════════════════════╗
# ║         🧠 rag_engine.py (AI Knowledge Base Engine)             ║
# ║                                                                  ║
# ║  [엔진 역할]                                                     ║
# ║  1. infra-master-lab의 기술 문서 자동 학습 (Ingestion)            ║
# ║  2. 사용자 질문에 관련된 최적의 지식 컨텍스트 검색 (Retrieval)     ║
# ╚══════════════════════════════════════════════════════════════════╝

import os
import logging
from typing import List
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RAG-Engine")

load_dotenv()

class RagEngine:
    def __init__(self, docs_path: str, persist_directory: str = "./data/chromadb"):
        self.docs_path = docs_path
        self.persist_directory = persist_directory
        # 로컬 임베딩 모델 초기화
        try:
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            logger.info("✅ HuggingFaceEmbeddings initialized successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize embeddings: {str(e)}")
            raise

        self.vector_db = None

    def ingest_docs(self):
        """지식 베이스 구축 (Ingestion)"""
        if not os.path.exists(self.docs_path):
            logger.error(f"❌ Source directory not found: {self.docs_path}")
            return

        try:
            logger.info(f"📂 Loading documents from: {self.docs_path}")
            loader = DirectoryLoader(self.docs_path, glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
            documents = loader.load()
            
            if not documents:
                logger.warning("⚠️ No documents found to ingest.")
                return

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = text_splitter.split_documents(documents)
            
            logger.info(f"🧠 Embedding {len(chunks)} chunks...")
            self.vector_db = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            logger.info("✅ Knowledge base built successfully!")
        except Exception as e:
            logger.error(f"❌ Ingestion failed: {str(e)}")

    def search_context(self, query: str, k: int = 3) -> str:
        """관련 컨텍스트 검색 (Retrieval)"""
        try:
            if not self.vector_db:
                if os.path.exists(self.persist_directory):
                    self.vector_db = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
                else:
                    logger.warning("⚠️ Vector DB not found. Returning empty context.")
                    return ""
                
            docs = self.vector_db.similarity_search(query, k=k)
            return "\n\n".join([doc.page_content for doc in docs])
        except Exception as e:
            logger.error(f"❌ Search failed: {str(e)}")
            return ""
