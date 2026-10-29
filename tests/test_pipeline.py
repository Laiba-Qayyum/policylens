from datetime import date
from pathlib import Path

import pytest

from src.ingestion import Chunk
from src.pipeline import ingest_files
from src.tenants import TenantStores


class FakeStore:
    def __init__(self) -> None:
        self.chunks: list[Chunk] = []

    def add(self, chunks: list[Chunk]) -> None:
        self.chunks.extend(chunks)

    def search(self, query: str, k: int = 3, min_score: float = -1.0) -> list[Chunk]:
        words = query.lower().split()
        return [c for c in self.chunks if any(w in c.text.lower() for w in words)][:k]


def write(folder: Path, name: str, text: str) -> Path:
    path = folder / name
    path.write_text(text, encoding="utf-8")
    return path


def test_ingest_files_adds_every_file_to_the_tenant(tmp_path: Path) -> None:
    a = write(tmp_path, "a.txt", "annual leave is 20 days")
    b = write(tmp_path, "b.txt", "remote work needs approval")
    stores = TenantStores(FakeStore)

    added = ingest_files(stores, "acme", [a, b])

    results = stores.search("acme", "leave remote")
    assert added == 2
    assert sorted(c.source for c in results) == ["a.txt", "b.txt"]
    assert stores.search("globex", "leave remote") == []


def test_ingest_files_uses_the_file_date_and_default_metadata(tmp_path: Path) -> None:
    a = write(tmp_path, "a.txt", "annual leave is 20 days")
    stores = TenantStores(FakeStore)

    ingest_files(stores, "acme", [a])

    chunk = stores.search("acme", "leave")[0]
    assert chunk.doc_type == "policy"
    assert chunk.version == "1.0"
    assert chunk.doc_date == date.today()


def test_ingest_files_adds_nothing_if_any_file_is_unsupported(tmp_path: Path) -> None:
    good = write(tmp_path, "a.txt", "annual leave is 20 days")
    bad = write(tmp_path, "b.exe", "not a document")
    stores = TenantStores(FakeStore)

    with pytest.raises(ValueError):
        ingest_files(stores, "acme", [good, bad])

    assert stores.search("acme", "leave") == []


def test_ingest_files_uses_the_explicit_date_when_given(tmp_path: Path) -> None:
    a = write(tmp_path, "a.txt", "annual leave is 20 days")
    stores = TenantStores(FakeStore)

    ingest_files(stores, "acme", [a], doc_dates={a: date(2025, 1, 1)})

    assert stores.search("acme", "leave")[0].doc_date == date(2025, 1, 1)
