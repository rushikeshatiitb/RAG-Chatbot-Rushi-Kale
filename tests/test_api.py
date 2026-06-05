from fastapi.testclient import TestClient

from sbi_fund_faq.api.main import create_app
from sbi_fund_faq.chatbot import REFUSAL_RESPONSE
from sbi_fund_faq.retrieval import NOT_FOUND_RESPONSE
from sbi_fund_faq.retrieval.vector_store import build_vector_store


def test_api_health():
    app = create_app()
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_query_factual():
    build_vector_store()
    app = create_app()
    client = TestClient(app)
    
    # We query about exit load of Flexicap Fund
    response = client.post(
        "/query",
        json={"question": "What is the exit load of SBI Flexicap Fund?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "What is the exit load of SBI Flexicap Fund?"
    assert "exit load" in data["answer"].lower()
    assert "Source: SBI Flexicap Fund Factsheet" in data["answer"]
    assert len(data["chunks"]) > 0
    assert data["is_advice"] is False
    assert data["is_ambiguous"] is False


def test_api_query_advice_refusal():
    build_vector_store()
    app = create_app()
    client = TestClient(app)
    
    response = client.post(
        "/query",
        json={"question": "Should I buy SBI Large Cap Fund?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == REFUSAL_RESPONSE
    assert len(data["chunks"]) == 0
    assert data["is_advice"] is True
    assert data["is_ambiguous"] is False


def test_api_query_ambiguous_scheme():
    build_vector_store()
    app = create_app()
    client = TestClient(app)
    
    response = client.post(
        "/query",
        json={"question": "What is the expense ratio?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "Please specify one of the supported schemes" in data["answer"]
    assert len(data["chunks"]) == 0
    assert data["is_advice"] is False
    assert data["is_ambiguous"] is True


def test_api_query_unsupported_field():
    build_vector_store()
    app = create_app()
    client = TestClient(app)
    
    response = client.post(
        "/query",
        json={"question": "What is the daily NAV of SBI Flexicap Fund?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == NOT_FOUND_RESPONSE
    assert len(data["chunks"]) == 0
    assert data["is_advice"] is False
    assert data["is_ambiguous"] is False
