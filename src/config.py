from pathlib import Path
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_backend: Literal["ollama", "openai"] = "ollama"
    openai_api_key: SecretStr | None = None
    data_dir: Path = Path("data")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    @model_validator(mode="after")
    def require_key_for_openai(self) -> "Settings":
        if self.llm_backend == "openai" and self.openai_api_key is None:
            raise ValueError("OPENAI_API_KEY is required when LLM_BACKEND=openai")
        return self
