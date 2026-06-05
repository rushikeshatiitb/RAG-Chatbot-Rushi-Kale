from sbi_fund_faq.ingestion.pipeline import run_ingestion


if __name__ == "__main__":
    result = run_ingestion()
    print(
        f"Ingested {result.chunk_count} chunks from "
        f"{result.source_count} approved sources into {result.output_path}"
    )
