import re
from pathlib import Path

from pypdf import PdfReader

from sbi_fund_faq.ingestion.models import IngestedChunk, clean_text
from sbi_fund_faq.ingestion.sources import SourceDocument


SECTION_PATTERNS = {
    "Investment Objective": (
        r"Investment Objective\s+(?P<section>.*?)\s+Fund Details"
    ),
    "Scheme Details": (
        r"\u2022\s+Type of Scheme\s+(?P<section>.*?\u2022\s+Additional Investment.*?)(?:PORTFOLIO|Pursuant|\^Investors)"
    ),
    "SIP and Investment Details": (
        r"(\u2022\s+)?SIP\s+(?P<section>.*?Minimum Investment.*?Additional Investment.*?)(?:PORTFOLIO|Pursuant|\^Investors)"
    ),
}


def parse_factsheet(source: SourceDocument, source_path: Path) -> list[IngestedChunk]:
    reader = PdfReader(str(source_path))
    chunks: list[IngestedChunk] = []
    scheme_name = source.scheme_names[0]

    for page_index, page in enumerate(reader.pages, start=1):
        page_text = clean_text(page.extract_text())
        if not page_text:
            continue

        chunks.append(
            IngestedChunk(
                id=f"{source.id}-page-{page_index}",
                source_name=source.source_name,
                scheme_name=scheme_name,
                document_type=source.document_type,
                document_month=source.document_month,
                page_number=page_index,
                section="Full Page Text",
                chunk_text=page_text,
                source_id=source.id,
                file_name=source.file_name,
            )
        )

        for section_name, pattern in SECTION_PATTERNS.items():
            section_text = extract_section(page_text, pattern)
            if section_text:
                chunks.append(
                    IngestedChunk(
                        id=f"{source.id}-page-{page_index}-{slug(section_name)}",
                        source_name=source.source_name,
                        scheme_name=scheme_name,
                        document_type=source.document_type,
                        document_month=source.document_month,
                        page_number=page_index,
                        section=section_name,
                        chunk_text=section_text,
                        source_id=source.id,
                        file_name=source.file_name,
                    )
                )

    return chunks


def extract_section(text: str, pattern: str) -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return ""
    return clean_section_text(match.group("section"))


def clean_section_text(value: str) -> str:
    text = clean_text(value)
    text = re.sub(r"^Quantitative Data\s+", "", text, flags=re.IGNORECASE)
    return text


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
