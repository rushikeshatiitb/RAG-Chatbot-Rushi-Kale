import re
from dataclasses import dataclass
from typing import Optional


SUPPORTED_SCHEMES = (
    "SBI Flexicap Fund",
    "SBI ELSS Tax Saver Fund",
    "SBI Large Cap Fund",
)

SCHEME_ALIASES = {
    "sbi flexicap": "SBI Flexicap Fund",
    "flexicap": "SBI Flexicap Fund",
    "flexi cap": "SBI Flexicap Fund",
    "sbi flexi cap": "SBI Flexicap Fund",
    "sbi elss": "SBI ELSS Tax Saver Fund",
    "elss": "SBI ELSS Tax Saver Fund",
    "tax saver": "SBI ELSS Tax Saver Fund",
    "tax saving": "SBI ELSS Tax Saver Fund",
    "sbi tax saver": "SBI ELSS Tax Saver Fund",
    "sbi large cap": "SBI Large Cap Fund",
    "large cap": "SBI Large Cap Fund",
    "largecap": "SBI Large Cap Fund",
    "sbi largecap": "SBI Large Cap Fund",
}

FIELD_ALIASES = {
    "expense ratio": "TER",
    "ter": "TER",
    "total expense ratio": "TER",
    "regular plan expense ratio": "TER",
    "direct plan expense ratio": "TER",
    "exit load": "exit load",
    "minimum sip": "minimum SIP amount",
    "sip minimum": "minimum SIP amount",
    "minimum sip amount": "minimum SIP amount",
    "minimum investment": "minimum application amount",
    "minimum investment amount": "minimum application amount",
    "minimum application amount": "minimum application amount",
    "benchmark": "benchmark index",
    "benchmark index": "benchmark index",
    "risk level": "riskometer",
    "riskometer": "riskometer",
    "lock in": "lock-in period",
    "lock-in": "lock-in period",
    "lock-in period": "lock-in period",
    "investment objective": "investment objective",
    "objective": "investment objective",
}


@dataclass(frozen=True)
class NormalizedQuery:
    original_query: str
    normalized_query: str
    scheme_name: Optional[str]
    field_name: Optional[str]
    is_ambiguous_scheme: bool = False


def normalize_query(query: str) -> NormalizedQuery:
    normalized_text = normalize_text(query)
    scheme_name, ambiguous = detect_scheme(normalized_text)
    field_name = detect_field(normalized_text)

    query_parts = [query.strip()]
    if scheme_name:
        query_parts.append(scheme_name)
    if field_name:
        query_parts.append(field_name)

    return NormalizedQuery(
        original_query=query,
        normalized_query=" ".join(part for part in query_parts if part),
        scheme_name=scheme_name,
        field_name=field_name,
        is_ambiguous_scheme=ambiguous,
    )


def detect_scheme(normalized_text: str) -> tuple[Optional[str], bool]:
    matches = {
        scheme
        for alias, scheme in SCHEME_ALIASES.items()
        if has_phrase(normalized_text, alias)
    }

    if len(matches) == 1:
        return next(iter(matches)), False
    if len(matches) > 1:
        return None, True
    if has_phrase(normalized_text, "sbi fund") or normalized_text.strip() in {"fund", "sbi"}:
        return None, True
    return None, False


def detect_field(normalized_text: str) -> Optional[str]:
    for alias in sorted(FIELD_ALIASES, key=len, reverse=True):
        if has_phrase(normalized_text, alias):
            return FIELD_ALIASES[alias]
    return None


def normalize_text(text: str) -> str:
    lowered = text.lower()
    lowered = lowered.replace("&", " and ")
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def has_phrase(text: str, phrase: str) -> bool:
    normalized_phrase = normalize_text(phrase)
    return re.search(rf"(^|\s){re.escape(normalized_phrase)}($|\s)", text) is not None
