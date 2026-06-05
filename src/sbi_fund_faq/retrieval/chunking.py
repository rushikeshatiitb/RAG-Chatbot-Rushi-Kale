import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from sbi_fund_faq.config import Settings, get_settings
from sbi_fund_faq.ingestion.models import clean_text
from sbi_fund_faq.ingestion.pipeline import DEFAULT_INGESTION_OUTPUT, run_ingestion
from sbi_fund_faq.ingestion.sources import load_source_registry


DEFAULT_RETRIEVAL_CHUNKS_OUTPUT = "retrieval_chunks.jsonl"
MAX_FULL_PAGE_CHARS = 1400
FULL_PAGE_OVERLAP_CHARS = 150


@dataclass(frozen=True)
class RetrievalChunk:
    id: str
    source_chunk_id: str
    source_id: str
    source_name: str
    scheme_name: str
    document_type: str
    document_month: str
    page_number: int
    section: str
    chunk_text: str
    file_name: str
    citation: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ChunkingResult:
    output_path: str
    chunk_count: int
    source_chunk_count: int


class ChunkValidationError(Exception):
    """Raised when retrieval chunks are missing required metadata."""


def run_chunking(settings: Optional[Settings] = None) -> ChunkingResult:
    settings = settings or get_settings()
    ingestion_path = settings.processed_data_dir / DEFAULT_INGESTION_OUTPUT
    if not ingestion_path.exists():
        run_ingestion(settings)

    source_chunks = read_jsonl(ingestion_path)
    retrieval_chunks = build_retrieval_chunks(source_chunks)
    validate_retrieval_chunks(retrieval_chunks, settings)

    output_path = settings.processed_data_dir / DEFAULT_RETRIEVAL_CHUNKS_OUTPUT
    write_jsonl(output_path, retrieval_chunks)

    return ChunkingResult(
        output_path=str(output_path),
        chunk_count=len(retrieval_chunks),
        source_chunk_count=len(source_chunks),
    )


def build_retrieval_chunks(source_chunks: list[dict[str, Any]]) -> list[RetrievalChunk]:
    chunks: list[RetrievalChunk] = []
    for source_chunk in source_chunks:
        chunk_text = clean_text(source_chunk.get("chunk_text"))
        if not chunk_text:
            continue

        if source_chunk.get("section") == "Full Page Text":
            text_parts = split_full_page_text(chunk_text)
        else:
            text_parts = [chunk_text]

        for part_index, text_part in enumerate(text_parts, start=1):
            chunks.append(create_retrieval_chunk(source_chunk, text_part, part_index))

    return chunks


def create_retrieval_chunk(
    source_chunk: dict[str, Any],
    chunk_text: str,
    part_index: int,
) -> RetrievalChunk:
    source_chunk_id = source_chunk["id"]
    section = source_chunk["section"]
    stable_input = "|".join(
        [
            source_chunk_id,
            str(part_index),
            source_chunk["source_id"],
            source_chunk["scheme_name"],
            section,
            chunk_text,
        ]
    )
    stable_hash = hashlib.sha256(stable_input.encode("utf-8")).hexdigest()[:16]
    page_number = int(source_chunk["page_number"])
    citation = build_citation(source_chunk, page_number)

    metadata = dict(source_chunk.get("metadata") or {})
    metadata.update(
        {
            "chunk_part": part_index,
            "citation": citation,
        }
    )

    return RetrievalChunk(
        id=f"{source_chunk_id}-part-{part_index}-{stable_hash}",
        source_chunk_id=source_chunk_id,
        source_id=source_chunk["source_id"],
        source_name=source_chunk["source_name"],
        scheme_name=source_chunk["scheme_name"],
        document_type=source_chunk["document_type"],
        document_month=source_chunk["document_month"],
        page_number=page_number,
        section=section,
        chunk_text=chunk_text,
        file_name=source_chunk["file_name"],
        citation=citation,
        metadata=metadata,
    )


def split_full_page_text(text: str) -> list[str]:
    if len(text) <= MAX_FULL_PAGE_CHARS:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + MAX_FULL_PAGE_CHARS, len(text))
        if end < len(text):
            boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = max(end - FULL_PAGE_OVERLAP_CHARS, 0)

    return [chunk for chunk in chunks if chunk]


def build_citation(source_chunk: dict[str, Any], page_number: int) -> str:
    source_name = source_chunk["source_name"]
    document_month = source_chunk["document_month"]
    section = source_chunk["section"]

    if source_chunk["document_type"] == "TER Data File":
        sheet_name = (source_chunk.get("metadata") or {}).get("sheet_name")
        row_number = (source_chunk.get("metadata") or {}).get("row_number")
        if sheet_name and row_number:
            return f"{source_name}, {sheet_name}, row {row_number}."
        return f"{source_name}."

    return f"{source_name}, {document_month}, page {page_number}, {section}."


def validate_retrieval_chunks(
    chunks: list[RetrievalChunk],
    settings: Optional[Settings] = None,
) -> None:
    settings = settings or get_settings()
    approved_source_ids = {source.id for source in load_source_registry(settings)}
    errors: list[str] = []
    seen_ids: set[str] = set()

    for chunk in chunks:
        if chunk.id in seen_ids:
            errors.append(f"Duplicate chunk id: {chunk.id}")
        seen_ids.add(chunk.id)

        if chunk.source_id not in approved_source_ids:
            errors.append(f"Unapproved source id: {chunk.source_id}")

        if not chunk.scheme_name:
            errors.append(f"Missing scheme name for chunk: {chunk.id}")

        if not chunk.citation:
            errors.append(f"Missing citation for chunk: {chunk.id}")

        if not chunk.chunk_text:
            errors.append(f"Missing chunk text for chunk: {chunk.id}")

    if errors:
        raise ChunkValidationError("; ".join(errors))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as input_file:
        return [
            json.loads(line)
            for line in input_file
            if line.strip()
        ]


def write_jsonl(output_path: Path, chunks: list[RetrievalChunk]) -> None:
    with output_path.open("w", encoding="utf-8") as output_file:
        for chunk in chunks:
            output_file.write(json.dumps(chunk.to_dict(), ensure_ascii=True))
            output_file.write("\n")
