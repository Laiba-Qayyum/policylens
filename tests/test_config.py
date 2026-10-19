from pathlib import Path

import pytest
from pydantic import ValidationError

from src.config import Settings

ENV_VARS = ["LLM_BACKEND", "OPENAI_API_KEY", "DATA_DIR", "LOG_LEVEL"]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)


def test_defaults() -> None:
    settings = Settings(_env_file=None)
    assert settings.llm_backend == "ollama"
    assert settings.data_dir == Path("data")
    assert settings.log_level == "INFO"


def test_reads_env_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("LLM_BACKEND=openai\nOPENAI_API_KEY=sk-test\nLOG_LEVEL=DEBUG\n")
    settings = Settings(_env_file=env_file)
    assert settings.llm_backend == "openai"
    assert settings.log_level == "DEBUG"


def test_api_key_is_hidden(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_BACKEND", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-secret")
    settings = Settings(_env_file=None)
    assert "sk-secret" not in repr(settings)
    assert settings.openai_api_key.get_secret_value() == "sk-secret"


def test_rejects_unknown_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_BACKEND", "gemini")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_openai_requires_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_BACKEND", "openai")
    with pytest.raises(ValidationError, match="OPENAI_API_KEY is required"):
        Settings(_env_file=None)
