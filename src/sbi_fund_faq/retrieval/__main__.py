from sbi_fund_faq.retrieval.chunking import run_chunking


if __name__ == "__main__":
    result = run_chunking()
    print(
        f"Created {result.chunk_count} retrieval chunks from "
        f"{result.source_chunk_count} ingested chunks into {result.output_path}"
    )
