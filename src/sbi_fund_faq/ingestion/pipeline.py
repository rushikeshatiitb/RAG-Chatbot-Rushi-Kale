import json
from pathlib import Path
from typing import Optional

from sbi_fund_faq.config import Settings, get_settings
from sbi_fund_faq.ingestion.factsheet_parser import parse_factsheet
from sbi_fund_faq.ingestion.models import IngestedChunk, IngestionResult
from sbi_fund_faq.ingestion.sources import (
    SourceDocument,
    validate_approved_sources,
)
from sbi_fund_faq.ingestion.ter_parser import parse_ter_file


DEFAULT_INGESTION_OUTPUT = "ingested_chunks.jsonl"


def run_ingestion(settings: Optional[Settings] = None) -> IngestionResult:
    settings = settings or get_settings()
    settings.processed_data_dir.mkdir(parents=True, exist_ok=True)

    sources = validate_approved_sources(settings)
    chunks: list[IngestedChunk] = []
    for source in sources:
        source_path = settings.source_docs_dir / source.file_name
        chunks.extend(parse_source(source, source_path))

    output_path = settings.processed_data_dir / DEFAULT_INGESTION_OUTPUT
    write_jsonl(output_path, chunks)

    return IngestionResult(
        output_path=str(output_path),
        chunk_count=len(chunks),
        source_count=len(sources),
    )


def parse_source(source: SourceDocument, source_path: Path) -> list[IngestedChunk]:
    if source.file_type == "pdf":
        return parse_factsheet(source, source_path)
    if source.file_type == "xlsx":
        return parse_ter_file(source, source_path)
    raise ValueError(f"Unsupported source file type: {source.file_type}")


def write_jsonl(output_path: Path, chunks: list[IngestedChunk]) -> None:
    with output_path.open("w", encoding="utf-8") as output_file:
        for chunk in chunks:
            output_file.write(json.dumps(chunk.to_dict(), ensure_ascii=True))
            output_file.write("\n")
