import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

# Mock env vars before importing main
import os
os.environ["OPENROUTER_API_KEY"] = "dummy"
os.environ["INFRA_DOCS_PATH"] = "/dummy/path"

with patch("main.RagEngine") as MockRag, patch("main.AgentBrain") as MockBrain:
    from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "online", "components": {"rag": "active", "agent": "active"}}

def test_ask_agent_empty_query():
    response = client.post("/ask", json={"query": ""})
    assert response.status_code == 400
    assert "Query cannot be empty" in response.json()["detail"]

@patch("main.brain")
def test_ask_agent_success(mock_brain):
    mock_brain.run.return_value = {"output": "Mocked AI Response"}
    
    response = client.post("/ask", json={"query": "테스트 질문입니다"})
    assert response.status_code == 200
    
    data = response.json()
    assert data["query"] == "테스트 질문입니다"
    assert data["answer"] == "Mocked AI Response"
    assert "metadata" in data
