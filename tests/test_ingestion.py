import json
from pathlib import Path

from sbi_fund_faq.ingestion.factsheet_parser import parse_factsheet
from sbi_fund_faq.ingestion.pipeline import run_ingestion
from sbi_fund_faq.ingestion.sources import load_source_registry
from sbi_fund_faq.ingestion.ter_parser import parse_ter_file


REQUIRED_CHUNK_FIELDS = {
    "source_name",
    "scheme_name",
    "document_type",
    "document_month",
    "page_number",
    "section",
    "chunk_text",
}


def test_run_ingestion_writes_intermediate_jsonl():
    result = run_ingestion()
    output_path = Path(result.output_path)

    assert output_path.exists()
    assert result.source_count == 4
    assert result.chunk_count > 4

    first_chunk = json.loads(output_path.read_text(encoding="utf-8").splitlines()[0])
    assert REQUIRED_CHUNK_FIELDS.issubset(first_chunk)


def test_factsheet_parser_preserves_supported_fact_fields():
    sources = {
        source.id: source
        for source in load_source_registry()
    }

    chunks = parse_factsheet(
        sources["sbi-flexicap-fund-factsheet-april-2026"],
        Path("data/source_docs/sbi-flexicap-fund-factsheet-april-2026.pdf"),
    )
    combined_text = " ".join(chunk.chunk_text for chunk in chunks)

    assert "First Tier Benchmark: BSE 500 (TRI)" in combined_text
    assert "Exit Load" in combined_text
    assert "Minimum Investment" in combined_text
    assert "SIP" in combined_text
    assert "To provide investors with opportunities" in combined_text


def test_factsheet_parser_extracts_scheme_details_section():
    source = next(
        source
        for source in load_source_registry()
        if source.id == "sbi-large-cap-fund-factsheet-april-2026"
    )

    chunks = parse_factsheet(
        source,
        Path("data/source_docs/sbi-large-cap-fund-factsheet-april-2026.pdf"),
    )
    scheme_details = [
        chunk for chunk in chunks
        if chunk.section == "Scheme Details"
    ]

    assert scheme_details
    assert "First Tier Benchmark: BSE 100 (TRI)" in scheme_details[0].chunk_text
    assert "Minimum Investment" in scheme_details[0].chunk_text


def test_ter_parser_maps_values_to_supported_schemes_and_plans():
    source = next(
        source
        for source in load_source_registry()
        if source.id == "sbi-total-expense-ratio-ter-data-file"
    )

    chunks = parse_ter_file(
        source,
        Path("data/source_docs/sbi-total-expense-ratio-ter-data-file.xlsx"),
    )

    assert chunks
    assert {chunk.scheme_name for chunk in chunks} == {
        "SBI Flexicap Fund",
        "SBI ELSS Tax Saver Fund",
        "SBI Large Cap Fund",
    }
    assert all(chunk.section == "Total Expense Ratio" for chunk in chunks)
    assert all("Regular Plan Total TER" in chunk.chunk_text for chunk in chunks)
    assert all("Direct Plan Total TER" in chunk.chunk_text for chunk in chunks)
    assert all(chunk.metadata["regular_plan_total_ter_percent"] for chunk in chunks)
    assert all(chunk.metadata["direct_plan_total_ter_percent"] for chunk in chunks)
