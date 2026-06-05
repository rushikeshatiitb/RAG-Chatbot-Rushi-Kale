from dataclasses import asdict, dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class IngestedChunk:
    id: str
    source_name: str
    scheme_name: str
    document_type: str
    document_month: str
    page_number: int
    section: str
    chunk_text: str
    source_id: str
    file_name: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IngestionResult:
    output_path: str
    chunk_count: int
    source_count: int


def clean_text(value: Optional[str]) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())
