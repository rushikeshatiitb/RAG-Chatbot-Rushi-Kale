import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from sbi_fund_faq.config import Settings, get_settings


@dataclass(frozen=True)
class SourceDocument:
    id: str
    source_name: str
    file_name: str
    document_type: str
    document_month: str
    scheme_names: list[str]
    file_type: str
    sha256: str

    @classmethod
    def from_registry_entry(cls, entry: dict[str, Any]) -> "SourceDocument":
        return cls(
            id=entry["id"],
            source_name=entry["source_name"],
            file_name=entry["file_name"],
            document_type=entry["document_type"],
            document_month=entry["document_month"],
            scheme_names=list(entry["scheme_names"]),
            file_type=entry["file_type"],
            sha256=entry["sha256"],
        )


class SourceValidationError(Exception):
    """Raised when approved source documents are missing or invalid."""


def load_source_registry(settings: Optional[Settings] = None) -> list[SourceDocument]:
    settings = settings or get_settings()
    registry_path = settings.source_registry_path

    with registry_path.open("r", encoding="utf-8") as registry_file:
        registry = json.load(registry_file)

    return [
        SourceDocument.from_registry_entry(entry)
        for entry in registry.get("approved_sources", [])
    ]


def approved_source_paths(settings: Optional[Settings] = None) -> dict[str, Path]:
    settings = settings or get_settings()
    return {
        source.id: settings.source_docs_dir / source.file_name
        for source in load_source_registry(settings)
    }


def validate_approved_sources(settings: Optional[Settings] = None) -> list[SourceDocument]:
    settings = settings or get_settings()
    sources = load_source_registry(settings)
    errors: list[str] = []

    for source in sources:
        source_path = settings.source_docs_dir / source.file_name
        if not source_path.exists():
            errors.append(f"Missing approved source: {source.file_name}")
            continue

        actual_sha256 = calculate_sha256(source_path)
        if actual_sha256 != source.sha256:
            errors.append(
                f"Checksum mismatch for {source.file_name}: "
                f"expected {source.sha256}, got {actual_sha256}"
            )

    if errors:
        raise SourceValidationError("; ".join(errors))

    return sources


def find_unapproved_source_files(settings: Optional[Settings] = None) -> list[Path]:
    settings = settings or get_settings()
    approved_file_names = {
        source.file_name
        for source in load_source_registry(settings)
    }

    return sorted(
        source_path
        for source_path in settings.source_docs_dir.iterdir()
        if source_path.is_file()
        and not source_path.name.startswith(".")
        and source_path.name not in approved_file_names
    )


def calculate_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
