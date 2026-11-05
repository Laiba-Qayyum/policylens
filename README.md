# PolicyLens

PolicyLens is a document question-answering system for organizations. It answers
questions from internal policies, handbooks and circulars using a local language
model, cites the source file and page, and says "I don't know" when the documents
don't support an answer. It flags documents that may compete (same type, different
date) and prefers the newest. Detecting real contradictions is planned.

> **Status:** in development, runs locally and in Docker. Loading, chunking, per-workspace
> search, answering through a local model, citation checking, a first check for competing
> documents, a command-line tool, an HTTP API with workspace keys, saved documents, an
> activity log and a Streamlit page work and are tested. A first test on three real
> documents is described below, including the failures that remain. Contradiction
> detection is planned. It is not ready for the public internet (see Limitations).

## Problem

Company rules are spread across many documents, and those documents often
disagree (for example, a 30-day and a 15-day return policy). People waste time
searching, and they can act on outdated or conflicting information.

## What works today

- **File loading:** reads TXT, DOCX and PDF files, keeping page numbers for PDFs.
- **Chunking:** splits text into overlapping chunks (200 words, 40 overlap by default).
- **Metadata:** each chunk carries its source file, page, document type, version
  and date. Files loaded through the command line or the API get type "policy" and
  version "1.0". The date is the file's modified time unless you give one (see below).
- **Semantic search:** chunks are embedded with a MiniLM model and searched with
  FAISS. A `min_score` cutoff drops chunks that are not similar enough.
- **Tenant isolation:** each tenant (workspace) has its own store. Tests check that one
  tenant never retrieves another tenant's text, including through the API.
- **Answering:** a numbered prompt is sent to a local model through Ollama. If nothing
  passes the cutoff, the system returns "I don't know." without calling the model.
- **Citation check:** the sources returned are the ones the reply cites like `[1]`.
  If the reply cites nothing, or cites a number that doesn't exist, the answer is
  returned marked `verified: false` and all retrieved sources are kept.
- **Competing sources:** when retrieved chunks come from different files of the same
  document type, the answer lists those files newest first, and the prompt marks the
  newest source and tells the model to prefer it and say that an older source differs.
  This uses metadata only. It does not check whether the texts really disagree.
- **Command line:** `scripts/ask.py` loads the files you name for a tenant and answers
  a question. `--file path@2025-01-01` sets a file's document date.
- **HTTP API:** `POST /tenants/{tenant_id}/documents` uploads files for a tenant and
  `POST /tenants/{tenant_id}/ask` answers a question, returning the answer, sources,
  competing files and the `verified` flag. An upload is all-or-nothing, and an
  unsupported file type returns a 400 error and adds nothing.
- **Workspaces and keys:** `POST /tenants` creates a workspace and returns a key once.
  Only a SHA-256 fingerprint of the key is stored (in `auth/registry.json` under the
  data folder). Every other request needs the key in an `X-API-Key` header, and a key
  opens only its own workspace. Keys set in `POLICYLENS_KEYS` are accepted too.
  Sign-up is open to anyone who can reach the server.
- **Saved documents:** each workspace's chunks are saved as JSON and reloaded after a
  restart. Uploading a file with the same name replaces its earlier chunks.
- **Document list and activity:** `GET /tenants/{id}/documents` lists files with chunk
  counts, and `GET /tenants/{id}/activity` returns recent events and counts. The
  activity log records uploads and questions but never the question text.
- **Web page:** a Streamlit page (`ui/`) with sign-up and sign-in (the key is shown
  once, with copy and download) and tabs for Overview, Ask, Documents and Activity.
  Tested with Streamlit's `AppTest` and checked by hand in a browser.
- **Evaluation script:** compares similarity cutoffs on a small set of labelled
  questions.
- **Configuration and logging:** validated settings; every log line includes a
  tenant ID.
- **Quality checks:** 216 pytest tests, ruff linting, pre-commit hooks that block
  committed secrets and `.env` files, and a GitHub Actions workflow that runs ruff
  and pytest.
- **Docker:** the image builds and runs the API as a non-root user with data in `/data`.
  Checked by hand with a volume: creating a workspace, signing in, restarting the
  container and signing in again worked, and a duplicate name was rejected. Earlier
  checks showed uploaded documents and the activity log surviving a restart. Answering
  from inside the container (it needs Ollama to be reachable) has not been checked.

## Evaluation (small samples)

**Similarity cutoff.** On 11 labelled questions over a six-sentence sample file (7
answerable, 4 unrelated), with only the top chunk counted:

| Cutoff | Answerable found | Unrelated refused |
|---|---|---|
| none | 7/7 | 0/4 |
| 0.15 | 7/7 | 4/4 |
| 0.30 | 6/7 | 4/4 |
| 0.50 | 5/7 | 4/4 |

This sample is far too small to prove a good cutoff for real documents. 0.15 is a
starting value to re-test on real files. Run it with
`python -m scripts.eval_cutoffs`.

**Competing documents.** Two one-sentence return policies (30 days and 15 days) and
the question "How many days do I have to return an item?", asked five times per
setting with `llama3.2:3b` through `scripts/ask.py`, with explicit document dates:

| Which file is newest | Right answer by the newest-date rule | Answers following it |
|---|---|---|
| The 15-day policy (2026) | 15 days | 5 of 5 |
| The 30-day policy (dates swapped) | 30 days | 5 of 5 |

In the swapped setting, one reply cited no source and was flagged unverified. The
15-day file was listed first in both settings, so the answers followed the date label,
not the position. This is one question on two tiny files, and a small local model
varies from run to run, so it shows the idea works, not that it is reliable. An
earlier comparison was withdrawn because both files had the same file-modified date.

**API check.** Against a real running server, uploading `samples/hr_policy.txt` for
tenant `acme` and asking about annual leave gave a correct answer with its source.
A parking question and the same leave question for a tenant with no documents both
returned "I don't know." This was checked by hand, before workspace keys were added,
and not by an automated test with the real model.

## Planned

1. Detecting real contradictions between documents (the current check uses metadata
   only), and preferring the authoritative one
2. Checking that a cited source actually supports the claim (today only its existence
   is checked)
3. Testing on real documents with a larger labelled set
4. Date and version fields in the upload API
5. Document delete, key rotation, rate limiting on sign-up and HTTPS
6. Checking answering from inside the Docker container

## Architecture

### Question-answering pipeline

```mermaid
flowchart LR
    A["Files<br/>TXT, DOCX, PDF"] --> B["Loaders<br/>src/loaders.py"]
    B --> C["Chunking<br/>src/chunking.py"]
    C --> D["Chunks with metadata<br/>src/ingestion.py, src/pipeline.py"]
    D --> E["Embeddings<br/>src/sbert_embedder.py"]
    E --> F["Per-tenant FAISS stores<br/>src/faiss_store.py, src/tenants.py"]
    F --> G["Prompt + local model<br/>src/prompts.py, src/ollama_llm.py"]
    G --> H["Answer, cited sources,<br/>competing files, verified flag<br/>src/answering.py, src/citations.py, src/conflicts.py"]
    H -.->|planned| I["Contradiction detection"]
    classDef planned stroke-dasharray: 5 5
    class I planned
```

Solid boxes are built; the dashed box is planned. The HTTP API (`src/api.py`) wraps
the upload and answering steps and checks workspace keys (`src/registry.py`), and
`src/main.py` runs it with the real components. The Streamlit page in `ui/` talks to
the API through `src/client.py`.

### How the parts connect

```mermaid
flowchart LR
    U["Browser"] --> P["Streamlit page<br/>ui/app.py, ui/signup.py"]
    P --> C["Client<br/>src/client.py"]
    C -->|"HTTP + X-API-Key"| API["FastAPI API<br/>src/api.py"]
    API --> R["Workspace registry<br/>src/registry.py"]
    API --> T["Per-workspace stores<br/>src/tenants.py + FAISS"]
    API --> L["Activity log<br/>src/activity.py"]
    API --> O["Ollama<br/>llama3.2:3b"]
    subgraph D["Data folder (/data in Docker)"]
        R --> RF["auth/registry.json<br/>key fingerprints only"]
        T --> TF["one JSON file per workspace<br/>saved chunks"]
        L --> LF["activity/*.jsonl<br/>no question text"]
    end
```

### Sign-up and sign-in

The server never stores a key. It stores only a SHA-256 fingerprint and compares
fingerprints when someone signs in.

```mermaid
sequenceDiagram
    actor User
    participant Page as Streamlit page
    participant API as FastAPI API
    participant Reg as Registry
    User->>Page: Company name
    Page->>API: POST /tenants with the workspace address
    API->>Reg: Create workspace
    Reg-->>API: New key, only its SHA-256 fingerprint is saved
    API-->>Page: Workspace and key, shown once
    Page-->>User: Key screen with copy and download
    Note over User,Page: Later, to sign in
    User->>Page: Workspace name and key
    Page->>API: GET documents with X-API-Key
    API->>Reg: Compare fingerprint of the key
    alt key matches the workspace
        API-->>Page: 200, signed in
    else wrong or missing key
        API-->>Page: 401 Invalid or missing API key
    end
```

### What happens when you ask a question

```mermaid
sequenceDiagram
    actor User
    participant API as FastAPI API
    participant Store as Workspace store
    participant LLM as Ollama model
    participant Log as Activity log
    User->>API: POST /tenants/acme/ask with X-API-Key
    API->>API: Check the key belongs to acme
    API->>Store: Search with the min_score cutoff
    alt nothing passes the cutoff
        API-->>User: I don't know, the model is not called
    else chunks found
        API->>LLM: Numbered prompt with the sources
        LLM-->>API: Reply citing sources like [1]
        API->>API: Check the cited numbers exist
        API-->>User: Answer, sources, competing files, verified flag
    end
    API->>Log: Record the event, never the question text
```

The citation check only confirms that a cited number exists. It does not confirm that
the source supports the answer (see Limitations).

## Getting started

Requires Python 3.11, Git, and [Ollama](https://ollama.com) for answering.

```powershell
git clone https://github.com/Laiba-Qayyum/policylens.git
cd policylens
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest
```

**Ask from the command line** (the first run downloads the embedding model):

```powershell
ollama pull llama3.2:3b
python -m scripts.ask --tenant acme --file samples/hr_policy.txt --question "How many days of annual leave do I get?"
```

Repeat `--file` to load several files, and add `@YYYY-MM-DD` to give a file its real
document date:

```powershell
python -m scripts.ask --tenant acme --file samples/returns_2025.txt@2025-01-01 --file samples/returns_2026.txt@2026-01-01 --question "How many days do I have to return an item?"
```

If the files look like competing versions of the same document, the output ends with a
note listing them, newest first. If the reply cites no valid source, it prints a
warning.

**Run the API.** Start the server in one terminal and leave it running:

```powershell
uvicorn src.main:app
```

In a second terminal, create a workspace. The key is returned once and the server keeps
only a fingerprint of it, so save it:

```powershell
$workspace = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/tenants -ContentType "application/json" -Body '{"name": "acme"}'
$key = $workspace.api_key
```

Then upload a file and ask a question with that key:

```powershell
curl.exe -H "X-API-Key: $key" -F "files=@samples/hr_policy.txt" http://127.0.0.1:8000/tenants/acme/documents
$body = '{"question": "How many days of annual leave do I get?"}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/tenants/acme/ask -Headers @{ "X-API-Key" = $key } -ContentType "application/json" -Body $body
```

Workspace names use lowercase letters, numbers, hyphens and underscores. A request
with a missing or wrong key gets a 401 error.

The interactive page at `http://127.0.0.1:8000/docs` works for asking questions, but
its file picker did not send files correctly in testing, so use `curl.exe` to upload.

**Run the web page.** With the API running, start the page from the project folder:

```powershell
python -m streamlit run ui\app.py
```

Create a workspace, save the key it shows (it appears once), then upload documents in
the Documents tab and ask in the Ask tab. Restart the page after changing code in
`src/` or `ui/`.

**Run with Docker.** Build the image and run it with a volume so workspaces and
documents survive restarts:

```powershell
docker build -t policylens:latest .
docker run --rm -p 8000:8000 -v policylens-data:/data policylens:latest
```

Answering from inside the container has not been checked, because it needs the
container to reach an Ollama server.

## Project structure

| Path | Purpose |
|---|---|
| `src/config.py` | Validated settings |
| `src/log.py` | Logging with tenant ID |
| `src/loaders.py` | TXT, DOCX and PDF loading |
| `src/chunking.py` | Overlapping text chunks |
| `src/ingestion.py` | Chunks with metadata |
| `src/pipeline.py` | Loads files into a tenant's store, all-or-nothing, with optional dates |
| `src/embeddings.py`, `src/sbert_embedder.py` | Embedder interface and MiniLM implementation |
| `src/vector_store.py`, `src/faiss_store.py` | Store interface and FAISS implementation |
| `src/tenants.py` | One store per tenant, saved to disk, replaces a file's chunks on re-upload |
| `src/registry.py` | Workspace names and key fingerprints (keys are never stored) |
| `src/activity.py` | Per-workspace activity log (no question text) |
| `src/conflicts.py` | Finds files that may compete (same type, different date) |
| `src/citations.py` | Finds which sources a reply cites and which citations are invalid |
| `src/prompts.py` | Builds the numbered prompt |
| `src/llm.py`, `src/ollama_llm.py` | Model interface and Ollama client |
| `src/answering.py` | Question to answer with sources |
| `src/cli.py` | Command-line options |
| `src/api.py` | HTTP endpoints: sign-up, upload, document list, activity, ask |
| `src/client.py` | Python client the web page uses to call the API |
| `src/main.py` | Runs the API with the real components |
| `src/evaluation.py` | Scores retrieval on labelled questions |
| `ui/app.py` | The dashboard page (Overview, Ask, Documents, Activity) |
| `ui/signup.py` | Sign-up and sign-in page, one-time key screen |
| `ui/components.py`, `ui/styles.py` | HTML cards and panels, and the page's CSS |
| `scripts/ask.py` | Ask a question about your files |
| `scripts/` (other) | Demos and the cutoff evaluation |
| `tests/` | pytest tests |
| `Dockerfile` | Builds the API image |
| `docs/decisions/` | Decision records |
| `PROBLEMS.md` | Problems encountered and how they were fixed |

## Development

Built with AI assistance (Claude) as a guide and reviewer, following a 10-day plan.
I write and run the code step by step, writing the test first, and I check results
against real test and script output. The problems I hit and how I fixed them are in
`PROBLEMS.md`.

## Testing on real documents

I tested on three public university policies (Greenwich staff expenses, Surrey flexible working, Nottingham travel expenses), each loaded into its own tenant. The PDFs are not in this repository. Before running anything I wrote ten questions with expected answers and pages, including two the documents do not answer.

A question counts as correct when the reply states the expected fact and the first source is the expected file. The page is tracked separately.

| Run | Correct |
|---|---|
| First run, before any change | 6 of 10 |
| After the Yes/No instruction, run 1 | 9 of 10 |
| After the Yes/No instruction, run 2 | 8 of 10 |

What I found: the answers to "Can I..." questions were being refused although retrieval had found the right text, and a code-level Yes/No instruction fixed that. The two questions the documents do not answer were refused correctly every time.

Still wrong or unverified:
- The appeal deadline question (Q6) fails: the right passage ranks too low and the model answers with a different rule.
- The page printed for one answer (Q4) is off by one. The verified flag only checks that a cited source number exists, not that the source supports the answer.
- I designed the Yes/No fix after seeing two of these ten questions fail, so these ten questions do not prove it works in general.
- Three documents, ten questions and two runs on a small local model (llama3.2:3b). Results may differ for other models and documents.
- A question counts as yes/no only if its first word is Can, Is, Do and similar. "Can you tell me how long...?" would be misclassified.

## Limitations

- Refusal depends partly on the model following the "I don't know" instruction.
- `verified` means the reply cites a source that exists, not that the source supports
  the claim. A reply can cite the wrong file and still count as verified.
- The cutoff of 0.15 comes from a very small sample and may not suit real documents.
- The competing-source check uses metadata only, so two unrelated files of the same
  type are also flagged.
- Preferring the newest source depends on the model. It followed the date label in
  five runs per setting on one tiny example, but a small local model can still get it
  wrong.
- Document dates come from the file's modified time unless you pass `--file path@date`.
  The API has no date field yet, so uploaded files get their upload time. The type and
  version are fixed defaults.
- Sign-up is open and has no rate limiting: anyone who can reach the server can create
  workspaces. There is no HTTPS, and keys cannot be recovered or rotated. Anyone
  holding a key has full access to that workspace. Do not expose this to the public
  internet as it is.
- Documents are saved as files on one machine. There is no database or backup, and
  documents cannot be deleted (uploading a file with the same name replaces it).
- Scanned PDFs (images of text) are not read, because there is no OCR.
- Only the happy path and unsupported file types are handled. A corrupt PDF or DOCX
  is not handled gracefully yet.
- Everything was tested on tiny sample files and three public PDFs, not on a large
  real document set.
- Needs a local Ollama server and model to answer.
- The design stores search indexes in memory on one machine, so it suits a single
  server, not thousands of customers. A larger deployment would need a
  database-backed store, background workers and load testing.