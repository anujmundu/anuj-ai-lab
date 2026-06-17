from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Anuj AI Lab"

    API_V1_PREFIX: str = "/api/v1"

    OLLAMA_BASE_URL: str = "http://localhost:11434"

    DEFAULT_MODEL: str = "qwen3.5:9b"

    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        env_file="../.env",
        extra="ignore"
    )


settings = Settings()