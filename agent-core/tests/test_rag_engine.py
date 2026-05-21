# -*- coding: utf-8 -*-
"""
🧠 test_rag_engine.py — RAG 엔진 단위 테스트

이 테스트 코드는 RAG 엔진(RagEngine)의 지식 베이스 빌드(Ingestion) 및 컨텍스트 검색(Retrieval)이
올바르게 작동하는지 검증합니다. 외부 리소스 및 네트워크 의존성을 제거하기 위해
HuggingFaceEmbeddings 및 ChromaDB 객체를 Mocking하여 테스트 환경을 격리합니다.

작성자: Hooney — AI FullStack Developer
"""

import os
import pytest
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from rag_engine import RagEngine


@pytest.fixture
def mock_embeddings():
    """HuggingFaceEmbeddings 모킹 피스처"""
    with patch("rag_engine.HuggingFaceEmbeddings") as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_class


def test_rag_engine_init_success(mock_embeddings):
    """
    RAG 엔진이 정상적으로 초기화되는지 검증합니다.
    """
    engine = RagEngine(docs_path="./test_docs", persist_directory="./test_data/chromadb")
    
    assert engine.docs_path == "./test_docs"
    assert engine.persist_directory == "./test_data/chromadb"
    mock_embeddings.assert_called_once_with(model_name="all-MiniLM-L6-v2")


def test_rag_engine_init_failure():
    """
    임베딩 모델 초기화 실패 시 예외가 발생하고 에러 로그가 기록되는지 검증합니다.
    """
    with patch("rag_engine.HuggingFaceEmbeddings", side_effect=Exception("Model Load Error")):
        with pytest.raises(Exception) as exc_info:
            RagEngine(docs_path="./test_docs")
        assert "Model Load Error" in str(exc_info.value)


def test_search_context_when_db_not_initialized_and_directory_missing(mock_embeddings):
    """
    벡터 DB가 빌드되지 않았고 영속화 디렉토리도 존재하지 않을 때,
    빈 컨텍스트("")를 반환하며 예외 없이 Fallback 처리되는지 검증합니다.
    """
    with patch("os.path.exists", return_value=False):
        engine = RagEngine(docs_path="./test_docs", persist_directory="./test_data/chromadb")
        context = engine.search_context("Test Query")
        assert context == ""


def test_search_context_load_from_persist_directory(mock_embeddings):
    """
    메모리에 벡터 DB가 없지만 영속화 디렉토리가 존재하는 경우,
    Chroma를 새로 로드하여 유사도 검색을 수행하는지 검증합니다.
    """
    engine = RagEngine(docs_path="./test_docs", persist_directory="./test_data/chromadb")
    
    # os.path.exists가 True를 반환하여 디렉토리가 있는 것으로 모킹
    with patch("os.path.exists", return_value=True), \
         patch("rag_engine.Chroma") as mock_chroma_class:
        
        mock_db_instance = MagicMock()
        mock_chroma_class.return_value = mock_db_instance
        
        # similarity_search 결과 문서 모킹
        mock_doc = Document(page_content="Mocked infrastructure document context")
        mock_db_instance.similarity_search.return_value = [mock_doc]
        
        context = engine.search_context("How to fix high CPU load?", k=1)
        
        # ChromaDB 로드 함수가 올바른 파라미터로 호출되었는지 확인
        mock_chroma_class.assert_called_once_with(
            persist_directory="./test_data/chromadb",
            embedding_function=engine.embeddings
        )
        # 검색 결과 검증
        assert context == "Mocked infrastructure document context"
        mock_db_instance.similarity_search.assert_called_once_with("How to fix high CPU load?", k=1)


def test_ingest_docs_no_directory(mock_embeddings):
    """
    소스 문서 디렉토리가 존재하지 않을 때, 경고를 남기고 Ingestion이 안전하게 조기 종료되는지 검증합니다.
    """
    engine = RagEngine(docs_path="./invalid_path", persist_directory="./test_data/chromadb")
    with patch("os.path.exists", return_value=False):
        # 예외 없이 실행이 끝나는지 확인
        engine.ingest_docs()
        assert engine.vector_db is None


def test_ingest_docs_success(mock_embeddings):
    """
    문서가 존재할 때 정상적으로 로드, 분할 및 ChromaDB 인덱싱이 성공하는지 검증합니다.
    """
    engine = RagEngine(docs_path="./test_docs", persist_directory="./test_data/chromadb")
    
    with patch("os.path.exists", return_value=True), \
         patch("rag_engine.DirectoryLoader") as mock_loader_class, \
         patch("rag_engine.RecursiveCharacterTextSplitter") as mock_splitter_class, \
         patch("rag_engine.Chroma.from_documents") as mock_from_documents:
        
        # Loader 모킹
        mock_loader = MagicMock()
        mock_loader.load.return_value = [Document(page_content="raw markdown document")]
        mock_loader_class.return_value = mock_loader
        
        # Splitter 모킹
        mock_splitter = MagicMock()
        mock_splitter.split_documents.return_value = [
            Document(page_content="chunk 1"),
            Document(page_content="chunk 2")
        ]
        mock_splitter_class.return_value = mock_splitter
        
        # Chroma 인스턴스 모킹
        mock_db_instance = MagicMock()
        mock_from_documents.return_value = mock_db_instance
        
        # 실행
        engine.ingest_docs()
        
        # 검증
        mock_loader.load.assert_called_once()
        mock_splitter.split_documents.assert_called_once()
        mock_from_documents.assert_called_once()
        assert engine.vector_db == mock_db_instance
