from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="SBI Mutual Fund FAQ Assistant", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    model_provider: str = Field(default="groq", alias="MODEL_PROVIDER")
    chat_model: str = Field(default="llama-3.3-70b-versatile", alias="CHAT_MODEL")
    groq_api_key: Optional[str] = Field(default=None, alias="GROQ_API_KEY")
    groq_api_base: str = Field(default="https://api.groq.com/openai/v1", alias="GROQ_API_BASE")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    local_embedding_dim: int = Field(default=384, alias="LOCAL_EMBEDDING_DIM")
    source_docs_dir: Path = Field(default=Path("data/source_docs"), alias="SOURCE_DOCS_DIR")
    source_registry_path: Path = Field(
        default=Path("data/source_registry.json"),
        alias="SOURCE_REGISTRY_PATH",
    )
    processed_data_dir: Path = Field(default=Path("data/processed"), alias="PROCESSED_DATA_DIR")
    vector_store_dir: Path = Field(default=Path("data/vector_store"), alias="VECTOR_STORE_DIR")
    host: str = Field(default="127.0.0.1", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
