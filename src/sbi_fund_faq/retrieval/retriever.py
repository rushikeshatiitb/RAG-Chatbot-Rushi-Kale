import re
from dataclasses import dataclass
from datetime import date
from typing import Optional

import numpy as np

from sbi_fund_faq.chatbot.guardrails import QuestionClassification, classify_question
from sbi_fund_faq.config import Settings, get_settings
from sbi_fund_faq.retrieval.normalization import NormalizedQuery, normalize_query
from sbi_fund_faq.retrieval.vector_store import (
    HashingEmbeddingModel,
    VectorRecord,
    load_vector_store,
)


NOT_FOUND_RESPONSE = "I could not find this information in the available approved SBI Mutual Fund sources."


@dataclass(frozen=True)
class RetrievedChunk:
    id: str
    score: float
    text: str
    metadata: dict


@dataclass(frozen=True)
class RetrievalResult:
    question: str
    classification: QuestionClassification
    normalized_query: NormalizedQuery
    chunks: list[RetrievedChunk]
    fallback_response: Optional[str] = None


class Retriever:
    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.records, self.embeddings = load_vector_store(self.settings)
        self.embedding_model = HashingEmbeddingModel(self.settings.local_embedding_dim)
        self.latest_ter_dates = latest_ter_dates_by_scheme(self.records)

    def retrieve(self, question: str, top_k: int = 4) -> RetrievalResult:
        classification = classify_question(question)
        normalized = normalize_query(question)

        if classification.is_advice:
            return RetrievalResult(
                question=question,
                classification=classification,
                normalized_query=normalized,
                chunks=[],
                fallback_response=classification.refusal_response,
            )

        if normalized.is_ambiguous_scheme:
            return RetrievalResult(
                question=question,
                classification=classification,
                normalized_query=normalized,
                chunks=[],
                fallback_response=(
                    "Please specify one of the supported schemes: SBI Flexicap Fund, "
                    "SBI ELSS Tax Saver Fund, or SBI Large Cap Fund."
                ),
            )

        if normalized.field_name is None:
            return RetrievalResult(
                question=question,
                classification=classification,
                normalized_query=normalized,
                chunks=[],
                fallback_response=NOT_FOUND_RESPONSE,
            )

        if normalized.scheme_name is None:
            return RetrievalResult(
                question=question,
                classification=classification,
                normalized_query=normalized,
                chunks=[],
                fallback_response=(
                    "Please specify one of the supported schemes: SBI Flexicap Fund, "
                    "SBI ELSS Tax Saver Fund, or SBI Large Cap Fund."
                ),
            )

        candidate_indexes = self._candidate_indexes(normalized)
        if not candidate_indexes:
            return RetrievalResult(
                question=question,
                classification=classification,
                normalized_query=normalized,
                chunks=[],
                fallback_response=NOT_FOUND_RESPONSE,
            )

        query_embedding = self.embedding_model.embed(normalized.normalized_query)
        scored_chunks = self._score_candidates(query_embedding, candidate_indexes, normalized)
        top_chunks = scored_chunks[:top_k]

        if not top_chunks or top_chunks[0].score < 0.08:
            return RetrievalResult(
                question=question,
                classification=classification,
                normalized_query=normalized,
                chunks=[],
                fallback_response=NOT_FOUND_RESPONSE,
            )

        return RetrievalResult(
            question=question,
            classification=classification,
            normalized_query=normalized,
            chunks=top_chunks,
        )

    def _candidate_indexes(self, normalized: NormalizedQuery) -> list[int]:
        indexes = []
        for index, record in enumerate(self.records):
            if normalized.scheme_name and record.metadata["scheme_name"] != normalized.scheme_name:
                continue
            indexes.append(index)
        return indexes

    def _score_candidates(
        self,
        query_embedding: np.ndarray,
        candidate_indexes: list[int],
        normalized: NormalizedQuery,
    ) -> list[RetrievedChunk]:
        scored: list[RetrievedChunk] = []
        for index in candidate_indexes:
            record = self.records[index]
            score = float(np.dot(query_embedding, self.embeddings[index]))
            score += field_boost(record, normalized.field_name)
            score += ter_date_boost(record, normalized.field_name, self.latest_ter_dates)
            score += section_boost(record)

            scored.append(
                RetrievedChunk(
                    id=record.id,
                    score=score,
                    text=record.text,
                    metadata=record.metadata,
                )
            )

        return sorted(scored, key=lambda chunk: chunk.score, reverse=True)


def retrieve(question: str, top_k: int = 4, settings: Optional[Settings] = None) -> RetrievalResult:
    return Retriever(settings).retrieve(question, top_k=top_k)


def field_boost(record: VectorRecord, field_name: Optional[str]) -> float:
    if not field_name:
        return 0.0

    text = f"{record.text} {record.metadata.get('section', '')}".lower()
    document_type = record.metadata.get("document_type")
    section = record.metadata.get("section")

    boosts = {
        "TER": 0.6 if document_type == "TER Data File" else 0.0,
        "exit load": 0.4 if "exit load" in text else 0.0,
        "minimum SIP amount": 0.4 if "sip" in text and "minimum" in text else 0.0,
        "minimum application amount": 0.4 if "minimum investment" in text else 0.0,
        "benchmark index": 0.4 if "benchmark" in text else 0.0,
        "riskometer": 0.3 if "risk" in text or "riskometer" in text else 0.0,
        "lock-in period": 0.4 if "lock-in" in text or "lock in" in text else 0.0,
        "investment objective": 0.5 if section == "Investment Objective" else 0.0,
    }
    return boosts.get(field_name, 0.0)


def section_boost(record: VectorRecord) -> float:
    section = record.metadata.get("section")
    if section in {"Scheme Details", "Investment Objective", "SIP and Investment Details", "Total Expense Ratio"}:
        return 0.05
    return 0.0


def latest_ter_dates_by_scheme(records: list[VectorRecord]) -> dict[str, date]:
    latest_dates: dict[str, date] = {}
    for record in records:
        if record.metadata.get("document_type") != "TER Data File":
            continue
        ter_date = parse_iso_date(record.text)
        if ter_date is None:
            continue
        scheme_name = record.metadata["scheme_name"]
        if scheme_name not in latest_dates or ter_date > latest_dates[scheme_name]:
            latest_dates[scheme_name] = ter_date
    return latest_dates


def ter_date_boost(
    record: VectorRecord,
    field_name: Optional[str],
    latest_ter_dates: dict[str, date],
) -> float:
    if field_name != "TER" or record.metadata.get("document_type") != "TER Data File":
        return 0.0

    ter_date = parse_iso_date(record.text)
    latest_date = latest_ter_dates.get(record.metadata["scheme_name"])
    if ter_date is None or latest_date is None:
        return 0.0
    if ter_date == latest_date:
        return 0.25
    return 0.0


def parse_iso_date(text: str) -> Optional[date]:
    match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None
