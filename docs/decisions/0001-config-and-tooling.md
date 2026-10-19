# 0001: Configuration and quality tooling

Date: 2026-10-20
Status: accepted

## Context
PolicyLens needs settings (LLM backend, API key, data folder, log level) that
change between my laptop, Docker and CI, without editing code. Secrets must
never reach Git, and every log line must show which tenant it belongs to.

## Decision
- One `Settings` class (pydantic-settings) reads environment variables, then
  `.env`, then defaults. Invalid values fail at startup. The API key is a
  `SecretStr`, so it is hidden in logs.
- Logging uses the standard `logging` module with `tenant_id` in every line
  through a `LoggerAdapter`.
- ruff for linting and formatting, pytest for tests, pre-commit to run ruff
  and block keys, `.env` files and large files before each commit.
- Direct dependencies are pinned with `==`.

## Alternatives considered
- `os.getenv` everywhere: no validation, values scattered across files.
- flake8 + black + isort: three tools where ruff does the same job.
- Pinning every sub-dependency with pip-tools: more reproducible, but an
  extra tool to explain. Can be added later if a sub-dependency breaks.

## Consequences
- Bad config is caught immediately with a clear error.
- Sub-dependencies are not pinned, so a fresh install months later could
  differ slightly.
