from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    PROJECT_NAME: str = "Anuj AI Lab"

    API_V1_PREFIX: str = "/api/v1"

    OLLAMA_BASE_URL: str = "http://localhost:11434"

    DEFAULT_MODEL: str = "qwen3.5:9b"

    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore"
    )


settings = Settings()