from sbi_fund_faq.chatbot.validator import validate_answer
from sbi_fund_faq.retrieval.retriever import RetrievedChunk
from sbi_fund_faq.retrieval import NOT_FOUND_RESPONSE


def test_validator_succeeds_with_valid_citation_and_grounded_numbers():
    chunk = RetrievedChunk(
        id="chunk_1",
        score=0.9,
        text="Regular Plan Total TER is 1.63% and Direct Plan Total TER is 0.82%. Minimum investment is 5000.",
        metadata={
            "citation": "SBI Flexicap Fund Factsheet, April 2026, page 1.",
        },
    )

    # All numbers (1.63%, 0.82%, 5000) are present in the chunk
    answer = "The regular expense ratio is 1.63% and minimum investment is 5000. Source: SBI Flexicap Fund Factsheet, April 2026, page 1."
    is_valid, final_answer = validate_answer(answer, [chunk])

    assert is_valid is True
    assert final_answer == answer


def test_validator_fails_when_citation_is_missing():
    chunk = RetrievedChunk(
        id="chunk_1",
        score=0.9,
        text="Regular Plan Total TER is 1.63%.",
        metadata={
            "citation": "SBI Flexicap Fund Factsheet, April 2026, page 1.",
        },
    )

    answer = "The regular expense ratio is 1.63%."
    is_valid, final_answer = validate_answer(answer, [chunk])

    assert is_valid is False
    assert final_answer == NOT_FOUND_RESPONSE


def test_validator_fails_when_citation_does_not_match_chunks():
    chunk = RetrievedChunk(
        id="chunk_1",
        score=0.9,
        text="Regular Plan Total TER is 1.63%.",
        metadata={
            "citation": "SBI Flexicap Fund Factsheet, April 2026, page 1.",
        },
    )

    # Citation refers to Large Cap Fund, which is not in the chunks
    answer = "The regular expense ratio is 1.63%. Source: SBI Large Cap Fund Factsheet, April 2026, page 2."
    is_valid, final_answer = validate_answer(answer, [chunk])

    assert is_valid is False
    assert final_answer == NOT_FOUND_RESPONSE


def test_validator_fails_on_hallucinated_percentage():
    chunk = RetrievedChunk(
        id="chunk_1",
        score=0.9,
        text="Regular Plan Total TER is 1.63%.",
        metadata={
            "citation": "SBI Flexicap Fund Factsheet, April 2026, page 1.",
        },
    )

    # Answer says expense ratio is 2.50% (hallucinated)
    answer = "The regular expense ratio is 2.50%. Source: SBI Flexicap Fund Factsheet, April 2026, page 1."
    is_valid, final_answer = validate_answer(answer, [chunk])

    assert is_valid is False
    assert final_answer == NOT_FOUND_RESPONSE


def test_validator_fails_on_hallucinated_large_number():
    chunk = RetrievedChunk(
        id="chunk_1",
        score=0.9,
        text="Minimum SIP is 500.",
        metadata={
            "citation": "SBI Flexicap Fund Factsheet, April 2026, page 1.",
        },
    )

    # Answer says minimum SIP is 5000 (hallucinated)
    answer = "The minimum SIP amount is 5000. Source: SBI Flexicap Fund Factsheet, April 2026, page 1."
    is_valid, final_answer = validate_answer(answer, [chunk])

    assert is_valid is False
    assert final_answer == NOT_FOUND_RESPONSE
