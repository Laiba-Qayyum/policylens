# PolicyLens

PolicyLens is a document question-answering system for organizations. It is
designed to answer questions from internal policies, handbooks, notices and
circulars, cite the source document and page, say "I don't know" when the
documents don't support an answer, and handle documents that contradict each
other.

- **Search:** FAISS search with a MiniLM embedder, using a separate store
  for each tenant. Tests check that tenants can only search their own documents.

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
- **Quality checks:** 27 pytest tests, ruff linting, and pre-commit hooks that
  block committed secrets and `.env` files.
- **Docker:** a Dockerfile is included (not yet built and tested end to end).

## Planned

1. Cited answers, refusing when documents don't support an answer
2. Conflict detection and preference for authoritative documents
3. Evaluation using measured results on a labeled test set
4. API and a simple web interface

## Architecture

```mermaid
flowchart LR
    A["Files<br/>TXT, DOCX, PDF"] --> B["Loaders<br/>src/loaders.py"]
    B --> C["Chunking<br/>src/chunking.py"]
    C --> D["Chunks with metadata<br/>src/ingestion.py"]
    D --> E["Per-tenant FAISS search<br/>src/tenants.py, src/faiss_store.py"]
    E -.->|planned| F["Cited answers"]
    classDef planned stroke-dasharray: 5 5
    class F planned
```

## Getting started

Requires Python 3.11 and Git.

```powershell
git clone https://github.com/Laiba-Qayyum/policylens.git
cd policylens
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

## Running tests

```powershell
pytest -v
ruff check .
```

## Project structure

| Path | Purpose |
|---|---|
| `src/config.py` | Validated settings |
| `src/log.py` | Logging with tenant ID |
| `src/loaders.py` | TXT, DOCX and PDF loading |
| `src/chunking.py` | Overlapping text chunks |
| `src/ingestion.py` | Chunks with metadata |
| `src/vector_store.py` | Store interface (`add`, `search`) |
| `src/tenants.py` | One store per tenant |
| `src/faiss_store.py` | FAISS store |
| `src/embeddings.py` | Embedder interface |
| `src/sbert_embedder.py` | MiniLM embedder |
| `scripts/search_demo.py` | Search demo on a sample policy |
| `tests/` | pytest tests |
| `docs/decisions/` | Decision records |
| `PROBLEMS.md` | Problems encountered and how they were fixed |

## Development

Developed with AI assistance using Claude Code, following a structured 10-day implementation plan. I defined the project scope, configured the development environment, and managed version control through Git and GitHub, with Docker incorporated into the workflow.

Development followed an iterative process of implementation, testing, debugging, and review. I investigated test failures, resolved environment and configuration issues, and addressed Git tracking and pre-commit hook problems to maintain code quality and a consistent development workflow. The key issues, resolutions, and lessons learned are documented in `PROBLEMS.md`.

## Limitations

- **Scanned PDFs:** there is no OCR. For image-only pages `extract_text()`
  returns an empty string, so the file produces no chunks and no error.
- **Metadata:** document type, version and date are not read from the
  document. The caller must pass them to `make_chunks`; they have no defaults.
- **DOCX:** only paragraphs are read, not tables. Page breaks are ignored, so
  the whole file is cited as page 1.
- **Chunk size:** `chunk_text` splits on whitespace, so the default size of
  200 (overlap 40) counts words, not characters or model tokens.
- **Not a question-answering system yet:** search and answering are planned.
- **Scalability:** the planned design stores search indexes on one machine, so
  it suits a single server, not thousands of customers. A larger deployment
  would need a database-backed store, background workers and load testing.
- Retrieval quality depends on chunk size. In the demo, a loosely related
  chunk ranked above the best match. This needs further evaluation.
