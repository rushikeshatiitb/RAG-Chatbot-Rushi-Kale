from sbi_fund_faq.retrieval.vector_store import build_vector_store


if __name__ == "__main__":
    result = build_vector_store()
    print(
        f"Built vector store with {result.record_count} records "
        f"and {result.embedding_dim}-dimensional embeddings."
    )
    print(f"Records: {result.records_path}")
    print(f"Embeddings: {result.embeddings_path}")
