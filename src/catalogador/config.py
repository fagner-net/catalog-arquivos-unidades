"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Typed configuration for the catalogador application."""

    database_url: str = "postgresql://localhost:5432/catalogador"
    log_level: str = "INFO"
    hash_chunk_size: int = 8192
    large_file_threshold_mb: int = 100

    model_config = {"env_prefix": "CATALOGADOR_"}


def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
