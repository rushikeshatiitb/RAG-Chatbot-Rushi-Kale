import pytest
from fastapi.testclient import TestClient

from sbi_fund_faq.api.main import create_app
from sbi_fund_faq.chatbot import REFUSAL_RESPONSE
from sbi_fund_faq.retrieval import NOT_FOUND_RESPONSE
from sbi_fund_faq.retrieval.vector_store import build_vector_store

# Supported schemes
SCHEMES = [
    "SBI Flexicap Fund",
    "SBI ELSS Tax Saver Fund",
    "SBI Large Cap Fund",
]

# Supported fields and query templates
FIELDS_TEMPLATES = {
    "expense ratio": "What is the expense ratio of {scheme}?",
    "exit load": "What is the exit load for {scheme}?",
    "minimum SIP amount": "What is the minimum SIP amount of {scheme}?",
    "minimum application amount": "What is the minimum investment amount for {scheme}?",
    "benchmark index": "What is the benchmark index of {scheme}?",
    "riskometer": "What is the risk level of {scheme}?",
    "lock-in period": "What is the lock-in period for {scheme}?",
    "investment objective": "What is the investment objective of {scheme}?",
}


@pytest.fixture(scope="module", autouse=True)
def init_vector_store():
    build_vector_store()


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


@pytest.mark.parametrize("scheme", SCHEMES)
@pytest.mark.parametrize("field_alias, query_template", list(FIELDS_TEMPLATES.items()))
def test_evaluation_factual_queries(client, scheme, field_alias, query_template):
    question = query_template.format(scheme=scheme)
    response = client.post("/query", json={"question": question})

    assert response.status_code == 200
    data = response.json()

    assert data["question"] == question
    assert data["is_advice"] is False
    assert data["is_ambiguous"] is False
    assert len(data["chunks"]) > 0

    # For schemes without lock-in period, they may return NOT_FOUND_RESPONSE in live mode
    if field_alias == "lock-in period" and scheme != "SBI ELSS Tax Saver Fund":
        if data["answer"] != NOT_FOUND_RESPONSE:
            assert scheme.lower() in data["answer"].lower()
            assert "Source:" in data["answer"]
    else:
        # Check that we received a valid, non-fallback answer and chunks
        assert data["answer"] != NOT_FOUND_RESPONSE
        assert data["answer"] != REFUSAL_RESPONSE
        # The scheme name should be explicitly mentioned in the answer
        assert scheme.lower() in data["answer"].lower()
        # Check citation format "Source: ..."
        assert "Source:" in data["answer"]


ADVICE_QUESTIONS = [
    "Should I invest in SBI Flexicap Fund?",
    "Which fund is the best to choose for my retirement?",
    "Should I buy or sell SBI Large Cap Fund?",
    "Can you recommend a good tax saver scheme?",
    "Should I buy or sell SBI ELSS Tax Saver Fund?",
]


@pytest.mark.parametrize("question", ADVICE_QUESTIONS)
def test_evaluation_advice_queries(client, question):
    response = client.post("/query", json={"question": question})

    assert response.status_code == 200
    data = response.json()
    assert data["question"] == question
    assert data["answer"] == REFUSAL_RESPONSE
    assert len(data["chunks"]) == 0
    assert data["is_advice"] is True
    assert data["is_ambiguous"] is False


MISSING_INFO_QUESTIONS = [
    "What is the daily NAV of SBI Flexicap Fund?",
    "Who is the CEO of SBI Mutual Fund?",
    "What is the historical returns for 2010 of SBI Large Cap Fund?",
    "How does SBI ELSS compare to HDFC Tax Saver in performance?",
]


@pytest.mark.parametrize("question", MISSING_INFO_QUESTIONS)
def test_evaluation_missing_info_queries(client, question):
    response = client.post("/query", json={"question": question})

    assert response.status_code == 200
    data = response.json()
    assert data["question"] == question
    assert data["answer"] == NOT_FOUND_RESPONSE
    assert len(data["chunks"]) == 0
    assert data["is_advice"] is False
    assert data["is_ambiguous"] is False
