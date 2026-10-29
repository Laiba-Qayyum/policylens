from datetime import date

from src.citations import cited_sources
from src.ingestion import Chunk


def make_chunks(count: int) -> list[Chunk]:
    return [
        Chunk(f"text {n}", "doc.txt", n, "policy", "1.0", date(2026, 1, 1))
        for n in range(1, count + 1)
    ]


def test_returns_only_the_cited_chunks_in_source_order() -> None:
    chunks = make_chunks(3)

    cited, invalid = cited_sources("Answer [3] and [1].", chunks)

    assert cited == [chunks[0], chunks[2]]
    assert invalid == []


def test_reports_citation_numbers_that_do_not_exist() -> None:
    chunks = make_chunks(2)

    cited, invalid = cited_sources("See [2] and [7].", chunks)

    assert cited == [chunks[1]]
    assert invalid == [7]


def test_a_reply_without_citations_cites_nothing() -> None:
    cited, invalid = cited_sources("No brackets here.", make_chunks(2))

    assert cited == []
    assert invalid == []


def test_the_same_citation_twice_counts_once() -> None:
    chunks = make_chunks(2)

    cited, _ = cited_sources("[1] says so, and [1] again.", chunks)

    assert cited == [chunks[0]]
