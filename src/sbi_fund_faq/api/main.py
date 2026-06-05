import logging
import time
from typing import Any, Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field

from sbi_fund_faq.config import get_settings, Settings
from sbi_fund_faq.retrieval.retriever import Retriever
from sbi_fund_faq.chatbot import generate_answer, validate_answer
from sbi_fund_faq.ingestion.sources import validate_approved_sources
from sbi_fund_faq.retrieval.vector_store import validate_vector_store

# Set up logging format and logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("sbi_fund_faq.api")


class QueryRequest(BaseModel):
    question: str = Field(..., description="The factual question about the mutual fund schemes.")


class ChunkMetadata(BaseModel):
    source_chunk_id: str
    source_id: str
    source_name: str
    scheme_name: Optional[str] = None
    document_type: str
    document_month: str
    page_number: int
    section: str
    file_name: str
    citation: str


class ChunkResponse(BaseModel):
    id: str
    score: float
    text: str
    metadata: ChunkMetadata


class QueryResponse(BaseModel):
    question: str
    answer: str
    chunks: list[ChunkResponse]
    is_advice: bool
    is_ambiguous: bool


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Phase 13: Startup validation checks
    try:
        validate_approved_sources(settings)
        validate_vector_store(settings)
        logger.info("Startup validation succeeded: Approved source documents and vector store are valid.")
    except Exception as e:
        logger.critical(f"Startup validation failed: {e}")
        raise RuntimeError(f"Startup validation failed: {e}") from e

    retriever = Retriever(settings)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "app": settings.app_name,
            "environment": settings.app_env,
        }

    @app.post("/query", response_model=QueryResponse)
    def query(request: QueryRequest) -> QueryResponse:
        start_time = time.time()
        logger.info(f"Received query request: '{request.question}'")

        result = retriever.retrieve(request.question)
        duration = time.time() - start_time

        logger.info(
            f"Retrieval completed in {duration:.4f}s. "
            f"Classification: is_advice={result.classification.is_advice}. "
            f"Ambiguous: is_ambiguous={result.normalized_query.is_ambiguous_scheme}. "
            f"Chunks retrieved: {len(result.chunks)}"
        )

        if result.fallback_response is not None:
            is_advice = result.classification.is_advice
            is_ambiguous = result.normalized_query.is_ambiguous_scheme or (
                not is_advice and result.normalized_query.scheme_name is None and "specify" in result.fallback_response
            )

            logger.info(f"Returning fallback response: '{result.fallback_response}'")
            return QueryResponse(
                question=request.question,
                answer=result.fallback_response,
                chunks=[],
                is_advice=is_advice,
                is_ambiguous=is_ambiguous,
            )

        # Generate answer using LLM / mock fallback
        generated = generate_answer(request.question, result.chunks, settings)

        # Validate the answer & citations
        is_valid, validated_answer = validate_answer(generated, result.chunks)

        logger.info(f"Answer generation completed. Grounding validation: is_valid={is_valid}")
        if not is_valid:
            logger.warning("Generated answer failed citation/grounding check; returning safe fallback response.")

        # Map RetrieveChunks to ChunkResponse schema
        response_chunks = [
            ChunkResponse(
                id=c.id,
                score=c.score,
                text=c.text,
                metadata=ChunkMetadata(
                    source_chunk_id=c.metadata["source_chunk_id"],
                    source_id=c.metadata["source_id"],
                    source_name=c.metadata["source_name"],
                    scheme_name=c.metadata.get("scheme_name"),
                    document_type=c.metadata["document_type"],
                    document_month=c.metadata["document_month"],
                    page_number=c.metadata["page_number"],
                    section=c.metadata["section"],
                    file_name=c.metadata["file_name"],
                    citation=c.metadata["citation"],
                ),
            )
            for c in result.chunks
        ]

        return QueryResponse(
            question=request.question,
            answer=validated_answer,
            chunks=response_chunks,
            is_advice=False,
            is_ambiguous=False,
        )

    return app

