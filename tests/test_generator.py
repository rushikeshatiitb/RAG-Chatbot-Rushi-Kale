import os
from unittest.mock import MagicMock, patch

from sbi_fund_faq.chatbot.generator import generate_answer, generate_mock_answer
from sbi_fund_faq.retrieval.retriever import RetrievedChunk
from sbi_fund_faq.retrieval import NOT_FOUND_RESPONSE
from sbi_fund_faq.config import Settings


def test_generator_returns_not_found_response_when_no_chunks():
    result = generate_answer("What is NAV?", [])
    assert result == NOT_FOUND_RESPONSE


def test_generator_mock_mode_expense_ratio():
    chunk = RetrievedChunk(
        id="chunk_1",
        score=0.8,
        text="SBI Large Cap Fund TER on 2026-06-04: Regular Plan Total TER 1.51%; Direct Plan Total TER 0.87%.",
        metadata={
            "citation": "SBI Total Expense Ratio (TER) Data File, Sheet1, row 7967.",
            "scheme_name": "SBI Large Cap Fund",
            "document_type": "TER Data File",
        },
    )
    result = generate_mock_answer("What is the expense ratio?", [chunk])
    assert "1.51% for the Regular Plan" in result
    assert "0.87% for the Direct Plan" in result
    assert "SBI Large Cap Fund" in result
    assert "Source: SBI Total Expense Ratio (TER) Data File, Sheet1, row 7967." in result


def test_generator_mock_mode_exit_load():
    chunk = RetrievedChunk(
        id="chunk_2",
        score=0.8,
        text="Exit Load: For exit on or before 30 days - 0.10%, for exit after 30 days - Nil",
        metadata={
            "citation": "SBI Flexicap Fund Factsheet, April 2026, page 1, Scheme Details.",
            "scheme_name": "SBI Flexicap Fund",
            "document_type": "Factsheet",
        },
    )
    result = generate_mock_answer("What is the exit load?", [chunk])
    assert "0.10%" in result
    assert "SBI Flexicap Fund" in result
    assert "Source: SBI Flexicap Fund Factsheet, April 2026, page 1, Scheme Details." in result


@patch.dict(os.environ, {"GROQ_API_KEY": "fake-groq-key"})
@patch("sbi_fund_faq.chatbot.generator.ChatOpenAI")
def test_generator_groq_called(mock_chat_openai):
    # Setup mock LLM response
    mock_instance = MagicMock()
    mock_chat_openai.return_value = mock_instance
    mock_response = MagicMock()
    mock_response.content = "Factual answer from Groq. Source: SBI Flexicap Fund Factsheet, April 2026, page 1."
    mock_instance.invoke.return_value = mock_response

    chunk = RetrievedChunk(
        id="chunk_1",
        score=0.9,
        text="Sample chunk text.",
        metadata={
            "citation": "SBI Flexicap Fund Factsheet, April 2026, page 1.",
            "scheme_name": "SBI Flexicap Fund",
            "document_type": "Factsheet",
        },
    )
    
    settings = Settings(MODEL_PROVIDER="groq", CHAT_MODEL="llama-3.3-70b-versatile")
    result = generate_answer("What is the exit load?", [chunk], settings=settings)
    
    assert result == "Factual answer from Groq. Source: SBI Flexicap Fund Factsheet, April 2026, page 1."
    mock_instance.invoke.assert_called_once()
    mock_chat_openai.assert_called_once_with(
        model="llama-3.3-70b-versatile",
        temperature=0.0,
        api_key="fake-groq-key",
        base_url="https://api.groq.com/openai/v1",
    )



@patch.dict(os.environ, {"OPENAI_API_KEY": "fake-openai-key"})
@patch("sbi_fund_faq.chatbot.generator.ChatOpenAI")
def test_generator_openai_called(mock_chat_openai):
    # Setup mock LLM response
    mock_instance = MagicMock()
    mock_chat_openai.return_value = mock_instance
    mock_response = MagicMock()
    mock_response.content = "Factual answer from OpenAI. Source: SBI Flexicap Fund Factsheet, April 2026, page 1."
    mock_instance.invoke.return_value = mock_response

    chunk = RetrievedChunk(
        id="chunk_1",
        score=0.9,
        text="Sample chunk text.",
        metadata={
            "citation": "SBI Flexicap Fund Factsheet, April 2026, page 1.",
            "scheme_name": "SBI Flexicap Fund",
            "document_type": "Factsheet",
        },
    )
    
    settings = Settings(MODEL_PROVIDER="openai", CHAT_MODEL="gpt-4o-mini")
    result = generate_answer("What is the exit load?", [chunk], settings=settings)
    
    assert result == "Factual answer from OpenAI. Source: SBI Flexicap Fund Factsheet, April 2026, page 1."
    mock_instance.invoke.assert_called_once()
    mock_chat_openai.assert_called_once_with(
        model="gpt-4o-mini",
        temperature=0.0,
        api_key="fake-openai-key",
        base_url=None,
    )

