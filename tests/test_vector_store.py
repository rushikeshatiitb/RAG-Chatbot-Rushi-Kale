from pathlib import Path

from sbi_fund_faq.config import get_settings
from sbi_fund_faq.retrieval.vector_store import (
    VECTOR_EMBEDDINGS_FILE,
    VECTOR_RECORDS_FILE,
    build_vector_store,
    load_vector_store,
    validate_vector_store,
)


def test_build_vector_store_writes_records_and_embeddings():
    result = build_vector_store()
    settings = get_settings()

    assert result.record_count > 0
    assert result.embedding_dim == settings.local_embedding_dim
    assert Path(result.records_path).name == VECTOR_RECORDS_FILE
    assert Path(result.embeddings_path).name == VECTOR_EMBEDDINGS_FILE
    assert Path(result.records_path).exists()
    assert Path(result.embeddings_path).exists()


def test_vector_store_records_include_required_metadata():
    build_vector_store()
    records, embeddings = load_vector_store()

    assert len(records) == len(embeddings)
    assert records[0].metadata["source_id"]
    assert records[0].metadata["source_name"]
    assert records[0].metadata["scheme_name"]
    assert records[0].metadata["citation"]


def test_vector_store_validates_successfully():
    build_vector_store()

    validate_vector_store()
