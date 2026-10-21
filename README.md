# PolicyLens

PolicyLens is a document question-answering system for organizations. It is
designed to answer questions from internal policies, handbooks, notices and
circulars, cite the source document and page, say "I don't know" when the
documents don't support an answer, and handle documents that contradict each
other.

> **Status:** in development. The document-processing foundation is done.
> Search, answering and conflict detection are planned.

## Problem

Company rules are spread across many documents, and those documents often
disagree (for example, a 30-day and a 15-day return policy). People waste time
searching, and they can act on outdated or conflicting information.

## What works today

- **File loading:** reads TXT, DOCX and PDF files, keeping page numbers for PDFs.
- **Chunking:** splits text into overlapping chunks so search can find the
  exact passage that answers a question.
- **Metadata:** each chunk carries its source file, page, document type,
  version and date.
- **Configuration:** one validated settings class that reads environment
  variables and hides the API key when printed.
- **Logging:** every log line includes a tenant ID.
- **Quality checks:** 21 pytest tests, ruff linting, and pre-commit hooks that
  block committed secrets and `.env` files.
- **Docker:** a Dockerfile that runs the app as a non-root user.

## Planned

1. Per-tenant document storage and search (tenant A must never retrieve
   tenant B's text, proven by a test)
2. Semantic search with FAISS, behind a small interface so the store can be
   swapped later
3. Cited answers, with refusal when the documents don't support one
4. Conflict detection between documents, and preferring the authoritative one
5. Evaluation with measured results on a labeled test set
6. API and a simple web interface

## Getting started

Requires Python 3.11 and Git.

```powershell
git clone https://github.com/Laiba-Qayyum/policylens.git
cd policylens
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest
```

## Project structure

| Path | Purpose |
|---|---|
| `src/config.py` | Validated settings |
| `src/log.py` | Logging with tenant ID |
| `src/loaders.py` | TXT, DOCX and PDF loading |
| `src/chunking.py` | Overlapping text chunks |
| `src/ingestion.py` | Chunks with metadata |
| `tests/` | pytest tests |
| `docs/decisions/` | Decision records |
| `PROBLEMS.md` | Problems encountered and how they were fixed |

## Development

Developed with AI assistance using Claude Code, following a structured 10-day implementation plan. I defined the project scope, configured the development environment, and managed version control through Git and GitHub, with Docker incorporated into the workflow.

Development followed an iterative process of implementation, testing, debugging, and review. I investigated test failures, resolved environment and configuration issues, and addressed Git tracking and pre-commit hook problems to maintain code quality and a consistent development workflow. The key issues, resolutions, and lessons learned are documented in `PROBLEMS.md`.

## Limitations

- Not a complete question-answering system yet.
- The planned design stores search indexes on one machine, so it suits a
  single server, not thousands of customers. A larger deployment would need a
  database-backed store, background workers and load testing.