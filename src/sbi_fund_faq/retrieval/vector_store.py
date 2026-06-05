import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

import numpy as np

from sbi_fund_faq.config import Settings, get_settings
from sbi_fund_faq.retrieval.chunking import (
    DEFAULT_RETRIEVAL_CHUNKS_OUTPUT,
    read_jsonl,
    run_chunking,
)
from sbi_fund_faq.ingestion.sources import load_source_registry


VECTOR_RECORDS_FILE = "records.json"
VECTOR_EMBEDDINGS_FILE = "embeddings.npy"


@dataclass(frozen=True)
class VectorRecord:
    id: str
    text: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VectorStoreBuildResult:
    record_count: int
    records_path: str
    embeddings_path: str
    embedding_dim: int


class VectorStoreValidationError(Exception):
    """Raised when vector store metadata is incomplete or unapproved."""


class HashingEmbeddingModel:
    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension

    def embed(self, text: str) -> np.ndarray:
        vector = np.zeros(self.dimension, dtype=np.float32)
        tokens = tokenize(text)
        if not tokens:
            return vector

        for token in tokens:
            vector[stable_hash(token) % self.dimension] += 1.0

        for first, second in zip(tokens, tokens[1:]):
            vector[stable_hash(f"{first}_{second}") % self.dimension] += 0.5

        norm = np.linalg.norm(vector)
        if norm:
            vector = vector / norm
        return vector

    def embed_many(self, texts: list[str]) -> np.ndarray:
        return np.vstack([self.embed(text) for text in texts]).astype(np.float32)


def build_vector_store(settings: Optional[Settings] = None) -> VectorStoreBuildResult:
    settings = settings or get_settings()
    retrieval_chunks_path = settings.processed_data_dir / DEFAULT_RETRIEVAL_CHUNKS_OUTPUT
    if not retrieval_chunks_path.exists():
        run_chunking(settings)

    retrieval_chunks = read_jsonl(retrieval_chunks_path)
    records = [
        VectorRecord(
            id=chunk["id"],
            text=chunk["chunk_text"],
            metadata={
                key: chunk[key]
                for key in (
                    "source_chunk_id",
                    "source_id",
                    "source_name",
                    "scheme_name",
                    "document_type",
                    "document_month",
                    "page_number",
                    "section",
                    "file_name",
                    "citation",
                )
            },
        )
        for chunk in retrieval_chunks
    ]

    validate_vector_records(records, settings)

    embedding_model = HashingEmbeddingModel(settings.local_embedding_dim)
    embeddings = embedding_model.embed_many([record.text for record in records])

    settings.vector_store_dir.mkdir(parents=True, exist_ok=True)
    records_path = settings.vector_store_dir / VECTOR_RECORDS_FILE
    embeddings_path = settings.vector_store_dir / VECTOR_EMBEDDINGS_FILE

    with records_path.open("w", encoding="utf-8") as records_file:
        json.dump([record.to_dict() for record in records], records_file, ensure_ascii=True, indent=2)
    np.save(embeddings_path, embeddings)

    validate_vector_store(settings)

    return VectorStoreBuildResult(
        record_count=len(records),
        records_path=str(records_path),
        embeddings_path=str(embeddings_path),
        embedding_dim=settings.local_embedding_dim,
    )


def load_vector_store(settings: Optional[Settings] = None) -> tuple[list[VectorRecord], np.ndarray]:
    settings = settings or get_settings()
    records_path = settings.vector_store_dir / VECTOR_RECORDS_FILE
    embeddings_path = settings.vector_store_dir / VECTOR_EMBEDDINGS_FILE

    if not records_path.exists() or not embeddings_path.exists():
        build_vector_store(settings)

    with records_path.open("r", encoding="utf-8") as records_file:
        records = [
            VectorRecord(
                id=record["id"],
                text=record["text"],
                metadata=record["metadata"],
            )
            for record in json.load(records_file)
        ]
    embeddings = np.load(embeddings_path)
    return records, embeddings


def validate_vector_store(settings: Optional[Settings] = None) -> None:
    settings = settings or get_settings()
    records, embeddings = load_vector_store_without_rebuild(settings)
    validate_vector_records(records, settings)

    if len(records) != len(embeddings):
        raise VectorStoreValidationError(
            f"Record count {len(records)} does not match embedding count {len(embeddings)}"
        )
    if embeddings.ndim != 2 or embeddings.shape[1] != settings.local_embedding_dim:
        raise VectorStoreValidationError("Embedding matrix has invalid dimensions")


def load_vector_store_without_rebuild(
    settings: Optional[Settings] = None,
) -> tuple[list[VectorRecord], np.ndarray]:
    settings = settings or get_settings()
    records_path = settings.vector_store_dir / VECTOR_RECORDS_FILE
    embeddings_path = settings.vector_store_dir / VECTOR_EMBEDDINGS_FILE

    with records_path.open("r", encoding="utf-8") as records_file:
        records = [
            VectorRecord(
                id=record["id"],
                text=record["text"],
                metadata=record["metadata"],
            )
            for record in json.load(records_file)
        ]
    return records, np.load(embeddings_path)


def validate_vector_records(
    records: list[VectorRecord],
    settings: Optional[Settings] = None,
) -> None:
    settings = settings or get_settings()
    approved_source_ids = {source.id for source in load_source_registry(settings)}
    required_metadata = {
        "source_id",
        "source_name",
        "scheme_name",
        "document_type",
        "document_month",
        "page_number",
        "section",
        "citation",
    }
    errors: list[str] = []
    seen_ids: set[str] = set()

    for record in records:
        if record.id in seen_ids:
            errors.append(f"Duplicate vector record id: {record.id}")
        seen_ids.add(record.id)

        missing = required_metadata - set(record.metadata)
        if missing:
            errors.append(f"Missing metadata {sorted(missing)} for {record.id}")

        if record.metadata.get("source_id") not in approved_source_ids:
            errors.append(f"Unapproved source id for {record.id}")

        if not record.text:
            errors.append(f"Missing text for {record.id}")

    if errors:
        raise VectorStoreValidationError("; ".join(errors))


def tokenize(text: str) -> list[str]:
    lowered = text.lower().replace("&", " and ")
    return re.findall(r"[a-z0-9]+", lowered)


def stable_hash(value: str) -> int:
    # FNV-1a keeps hashes stable across Python processes.
    hash_value = 2166136261
    for character in value:
        hash_value ^= ord(character)
        hash_value = (hash_value * 16777619) % int(math.pow(2, 32))
    return hash_value
