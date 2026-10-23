# Problems and Lessons

A record of real problems hit while building PolicyLens, how each was diagnosed and fixed, and what was learned. Planned challenges are listed separately at the end.

## Problems encountered

| Date | Problem | Cause | Resolution | Lesson |
|---|---|---|---|---|
| 21 Oct 2026 | `docker` not recognized in PowerShell | The terminal was opened before Docker was installed, so its PATH was stale. | Added the Docker folder to PATH for that session; restarting the terminal fixes it permanently. | A new install is not visible to terminals that were already open. |
| 21 Oct 2026 | `pytest` failed with "No module named 'src'" | Tests were run from the parent folder, not the project root, so the configured import path was not applied. | Changed into the project folder before running tests. | Run tools from the project root, and check the working directory first. |
| 21 Oct 2026 | Loader tests were missing | `test_loaders.py` was empty, and later held loader code instead of tests. | Replaced it with the correct tests and re-ran the suite. | Confirm a file's contents after saving it, not just that it exists. |
| 22 Oct 2026 | First commit failed after the formatter ran | The ruff-format hook rewrote files and stopped the commit, so the next push reported "Everything up-to-date". | Staged the reformatted files and committed again. | If a hook modifies files, re-add and recommit before pushing. |
| 22 Oct 2026 | `git` reported "not a repository" | Commands were run from the workspace folder above the project. | Changed into the project folder and re-ran them. | Check the prompt's folder before running Git commands. |
| 22 Oct 2026 | Git tag pointed at the wrong commit | The commit, push and tag commands were pasted together. The hook stopped the commit, but the tag command still ran on the previous commit and was pushed. | Moved the tag with `git tag -f` and updated it on GitHub with a forced tag push. | A failed commit does not stop later commands. Run them one at a time and confirm the commit before tagging. |
| 22 Oct 2026 | Search demo raised `FileNotFoundError` | The sample file was inside a nested `samples/samples` folder. | Moved the file up one level and removed the empty folder. | Confirm exact paths with `dir` before running a script that reads files. |
| 22 Oct 2026 | Embedding model download stalled | On a slow connection the download paused at the file-assembly step. | Stopped the run, disabled the fast-download helper for that session, and restarted. Partial downloads were reused. | Check whether bytes are still moving before retrying, and know the fallback. |
| 22 Oct 2026 | Search ranked a less relevant chunk first | Chunks were small (20 words), cut across sentences, and a loosely related chunk shared the word "days" with the question. The best chunk ranked second. | Not fixed. Recorded as a limitation. Chunk size has not yet been tested systematically. | Measure retrieval quality before building answer generation on top of it. |

## Challenges ahead

These are planned, not yet encountered. Each one should end in a reproducible test.

| Challenge | Why it matters | Planned approach | Planned validation |
|---|---|---|---|
| Preserving PDF page-level traceability | Wrong page metadata makes citations point to the wrong place. | Carry page numbers through extraction, chunking and retrieval. | Test multi-page PDFs against their original pages. |
| Handling malformed and partially readable documents | One corrupted file should not crash a whole ingestion batch. | Validate file types and handle parsing errors per document. | Test empty, malformed, unsupported and partly readable files. |
| Avoiding unsupported answers | A language model can produce plausible text that the sources don't support. | Require evidence, apply relevance thresholds, and abstain when evidence is weak. | Test questions with and without available evidence. |
| Maintaining citations through chunking | Overlapping chunks can cause duplicated or incomplete citations. | Attach source and page metadata to each chunk and return it with results. | Check citations on documents with repeated text. |
| Detecting conflicting policy statements | Two documents can disagree because of version changes or different scope. | Compare relevant passages with document dates and versions before flagging. | Test known conflicts and cases that only look contradictory. |
| Keeping ingestion repeatable | Re-ingesting a document can create duplicate chunks. | Use stable document IDs and content hashes with explicit re-ingestion rules. | Ingest the same file twice and check the record counts. |
| Controlling resource use for large documents | Large PDFs can increase memory use and processing time. | Process incrementally, configure chunk sizes and set file-size limits. | Benchmark representative sizes for time and memory. |

Principle: a fix is complete only when the relevant test passes and the expected behavior is documented.