import json
from pathlib import Path

from sbi_fund_faq.retrieval.chunking import (
    build_retrieval_chunks,
    read_jsonl,
    run_chunking,
    validate_retrieval_chunks,
)


REQUIRED_RETRIEVAL_FIELDS = {
    "id",
    "source_chunk_id",
    "source_id",
    "source_name",
    "scheme_name",
    "document_type",
    "document_month",
    "page_number",
    "section",
    "chunk_text",
    "file_name",
    "citation",
    "metadata",
}


def test_run_chunking_writes_retrieval_chunks_jsonl():
    result = run_chunking()
    output_path = Path(result.output_path)

    assert output_path.exists()
    assert result.source_chunk_count > 0
    assert result.chunk_count >= result.source_chunk_count

    first_chunk = json.loads(output_path.read_text(encoding="utf-8").splitlines()[0])
    assert REQUIRED_RETRIEVAL_FIELDS.issubset(first_chunk)


def test_chunk_ids_are_stable_for_same_source_chunks():
    source_chunks = read_jsonl(Path("data/processed/ingested_chunks.jsonl"))

    first_run_ids = [chunk.id for chunk in build_retrieval_chunks(source_chunks)]
    second_run_ids = [chunk.id for chunk in build_retrieval_chunks(source_chunks)]

    assert first_run_ids == second_run_ids


def test_retrieval_chunks_have_citation_metadata():
    result = run_chunking()
    chunks = read_jsonl(Path(result.output_path))

    assert chunks
    assert all(chunk["citation"] for chunk in chunks)
    assert all(chunk["metadata"]["citation"] == chunk["citation"] for chunk in chunks)
    assert all(chunk["source_name"] in chunk["citation"] for chunk in chunks)


def test_scheme_specific_chunks_do_not_mix_supported_schemes():
    result = run_chunking()
    chunks = read_jsonl(Path(result.output_path))
    supported_schemes = {
        "SBI Flexicap Fund",
        "SBI ELSS Tax Saver Fund",
        "SBI Large Cap Fund",
    }

    for chunk in chunks:
        other_schemes = supported_schemes - {chunk["scheme_name"]}
        assert not any(other_scheme in chunk["chunk_text"] for other_scheme in other_schemes)


def test_important_facts_remain_together_in_scheme_details_chunks():
    result = run_chunking()
    chunks = read_jsonl(Path(result.output_path))
    scheme_detail_chunks = [
        chunk
        for chunk in chunks
        if chunk["scheme_name"] == "SBI Large Cap Fund"
        and chunk["section"] == "Scheme Details"
    ]

    assert scheme_detail_chunks
    chunk_text = scheme_detail_chunks[0]["chunk_text"]
    assert "First Tier Benchmark: BSE 100 (TRI)" in chunk_text
    assert "Exit Load" in chunk_text
    assert "Minimum Investment" in chunk_text


def test_retrieval_chunk_validation_accepts_generated_chunks():
    source_chunks = read_jsonl(Path("data/processed/ingested_chunks.jsonl"))
    chunks = build_retrieval_chunks(source_chunks)

    validate_retrieval_chunks(chunks)
