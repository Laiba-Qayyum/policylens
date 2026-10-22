## Engineering Challenges & Lessons Learned

PolicyLens processes documents that may contain inconsistent formatting, incomplete metadata, and conflicting policy statements. The following challenges guide implementation and validation as the project evolves.

| Challenge | Why It Matters | Engineering Approach | Validation |
|---|---|---|---|
| Preserving PDF page-level traceability | Incorrect page metadata can make citations point to the wrong location, reducing trust in answers. | Preserve page numbers during extraction and carry them through chunking and retrieval. | Test multi-page PDFs and verify every retrieved chunk against its original page. |
| Handling malformed and partially readable documents | A single unsupported or corrupted file should not crash an entire ingestion batch. | Validate file types, handle parsing errors per document, and record actionable error details. | Test empty, malformed, unsupported, and partially readable files. |
| Preventing retrieval from crossing tenant boundaries | Shared indexes or incorrectly applied filters could expose one tenant's documents to another. | Enforce tenant-scoped retrieval and authorization at the data-access layer. | Add isolation tests proving that one tenant cannot retrieve another tenant's chunks. |
| Avoiding unsupported answers | A language model may generate plausible statements that are not supported by the source documents. | Require evidence-based answers, apply relevance thresholds, and abstain when retrieved evidence is insufficient. | Test answer generation against questions with both available and unavailable evidence. |
| Maintaining citations through chunking | Overlapping chunks and document transformations can cause duplicated or incomplete citations. | Attach stable source identifiers and page metadata to each chunk; return source references with retrieved passages. | Verify citation accuracy for documents with repeated text and overlapping chunks. |
| Detecting conflicting policy statements | Two documents may give different instructions because of version changes, exceptions, or inconsistent wording. | Compare relevant passages alongside document dates, versions, and source metadata before flagging a conflict. | Test known conflicting statements and cases that appear contradictory but have different scopes. |
| Keeping ingestion reliable and repeatable | Reprocessing the same documents can create duplicate chunks or inconsistent index contents. | Use stable document identifiers, content hashes, and explicit re-ingestion rules. | Ingest the same document twice and verify the expected record counts and results. |
| Controlling resource usage for large documents | Large PDFs or bulk uploads can increase memory usage and processing time. | Process documents incrementally, configure chunk sizes, and establish file-size limits. | Benchmark representative document sizes and measure processing time and memory usage. |

### Engineering Principle

Every challenge should lead to a reproducible test. A fix is considered complete only when the relevant test passes and the expected behavior is documented.
