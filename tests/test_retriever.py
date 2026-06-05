from sbi_fund_faq.chatbot.guardrails import REFUSAL_RESPONSE
from sbi_fund_faq.retrieval import NOT_FOUND_RESPONSE, Retriever
from sbi_fund_faq.retrieval.retriever import parse_iso_date
from sbi_fund_faq.retrieval.vector_store import build_vector_store


def test_retriever_returns_ter_chunks_for_expense_ratio():
    build_vector_store()
    retriever = Retriever()
    result = retriever.retrieve("What is the expense ratio of SBI Flexicap Fund?")

    assert result.fallback_response is None
    assert result.chunks
    top_chunk = result.chunks[0]
    assert top_chunk.metadata["scheme_name"] == "SBI Flexicap Fund"
    assert top_chunk.metadata["document_type"] == "TER Data File"
    assert "Total TER" in top_chunk.text
    assert parse_iso_date(top_chunk.text) == retriever.latest_ter_dates["SBI Flexicap Fund"]


def test_retriever_returns_factsheet_chunks_for_benchmark():
    build_vector_store()
    result = Retriever().retrieve("What is the benchmark index for SBI Large Cap Fund?")

    assert result.fallback_response is None
    assert result.chunks
    top_chunk = result.chunks[0]
    assert top_chunk.metadata["scheme_name"] == "SBI Large Cap Fund"
    assert top_chunk.metadata["document_type"] == "Factsheet"
    assert "BSE 100 (TRI)" in top_chunk.text
    assert top_chunk.metadata["citation"]


def test_retriever_refuses_advice_before_retrieval():
    build_vector_store()
    result = Retriever().retrieve("Should I invest in SBI ELSS Tax Saver Fund?")

    assert result.fallback_response == REFUSAL_RESPONSE
    assert result.chunks == []


def test_retriever_asks_for_scheme_when_query_is_ambiguous():
    build_vector_store()
    result = Retriever().retrieve("What is the expense ratio of SBI fund?")

    assert result.chunks == []
    assert "Please specify" in result.fallback_response


def test_retriever_returns_not_found_for_unsupported_query_without_scheme():
    build_vector_store()
    result = Retriever().retrieve("What is today's NAV?")

    assert result.chunks == []
    assert result.fallback_response == NOT_FOUND_RESPONSE
