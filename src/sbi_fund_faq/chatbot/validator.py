"""Citation and grounding validation module for generated answers."""

import re
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from sbi_fund_faq.retrieval.retriever import RetrievedChunk

NOT_FOUND_RESPONSE = "I could not find this information in the available approved SBI Mutual Fund sources."


def validate_answer(answer: str, chunks: list["RetrievedChunk"]) -> tuple[bool, str]:
    """Validate that the answer includes a citation to an approved retrieved chunk and is grounded.

    Returns:
        A tuple of (is_valid, final_answer). If invalid, final_answer is the fallback response.
    """
    if not chunks:
        return False, NOT_FOUND_RESPONSE

    # 1. Extract citation
    # Look for "Source: <citation>"
    match = re.search(r"Source:\s*(.+)$", answer, re.IGNORECASE)
    if not match:
        return False, NOT_FOUND_RESPONSE

    citation_text = match.group(1).strip()

    # 2. Check if the citation matches any retrieved chunk's citation
    valid_citation = False
    for chunk in chunks:
        chunk_citation = chunk.metadata.get("citation", "")
        if not chunk_citation:
            continue
        # Check if the extracted citation is contained within or contains the chunk citation (case-insensitive)
        if (
            citation_text.lower() in chunk_citation.lower()
            or chunk_citation.lower() in citation_text.lower()
        ):
            valid_citation = True
            break

    if not valid_citation:
        return False, NOT_FOUND_RESPONSE

    # 3. Grounding check:
    # Remove the citation suffix before searching numbers to avoid checking page numbers or years in citation
    answer_body = answer[:match.start()].strip()

    numbers_to_check = []

    # Extract percentages: e.g. 1.63%, 0.10%
    percentages = re.findall(r"\b\d+(?:\.\d+)?%\b", answer_body)
    numbers_to_check.extend(percentages)

    # Extract decimals: e.g. 1.63, 0.82
    decimals = re.findall(r"\b\d+\.\d+\b", answer_body)
    numbers_to_check.extend(decimals)

    # Extract integers (length > 1, excluding common dates/years and single digits)
    integers = re.findall(r"\b\d{2,}\b", answer_body)
    ignored_vals = {"2026", "2025", "2024", "2005", "30", "18", "19", "29", "12", "10"}
    for val in integers:
        if val not in ignored_vals:
            numbers_to_check.append(val)

    # Combine chunk texts to check against
    combined_chunks_text = " ".join(chunk.text for chunk in chunks)

    # Check that every extracted number exists in the chunk texts
    for num in numbers_to_check:
        if num not in combined_chunks_text:
            return False, NOT_FOUND_RESPONSE

    return True, answer
