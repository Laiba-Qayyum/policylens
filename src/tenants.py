import json
import re
from collections.abc import Callable
from dataclasses import asdict
from datetime import date
from pathlib import Path

from src.ingestion import Chunk
from src.vector_store import VectorStore

SAFE_ID = re.compile(r"[A-Za-z0-9_-]{1,64}")


def _write(path: Path, chunks: list[Chunk]) -> None:
    data = [{**asdict(c), "doc_date": c.doc_date.isoformat()} for c in chunks]
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data), encoding="utf-8")
    temp.replace(path)


def _read(path: Path) -> list[Chunk]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Chunk(**{**d, "doc_date": date.fromisoformat(d["doc_date"])}) for d in data]


class TenantStores:
    def __init__(
        self, store_factory: Callable[[], VectorStore], directory: Path | None = None
    ) -> None:
        self._factory = store_factory
        self._directory = directory
        self._stores: dict[str, VectorStore] = {}
        self._chunks: dict[str, list[Chunk]] = {}
        if directory is not None:
            directory.mkdir(parents=True, exist_ok=True)
            for file in sorted(directory.glob("*.json")):
                if SAFE_ID.fullmatch(file.stem):
                    self._add(file.stem, _read(file))

    def _add(self, tenant_id: str, chunks: list[Chunk]) -> None:
        if tenant_id not in self._stores:
            self._stores[tenant_id] = self._factory()
            self._chunks[tenant_id] = []
        self._stores[tenant_id].add(chunks)
        self._chunks[tenant_id].extend(chunks)

    def add(self, tenant_id: str, chunks: list[Chunk]) -> None:
        if self._directory is not None and not SAFE_ID.fullmatch(tenant_id):
            raise ValueError(f"invalid tenant id: {tenant_id!r}")
        self._add(tenant_id, chunks)
        if self._directory is not None:
            _write(self._directory / f"{tenant_id}.json", self._chunks[tenant_id])

    def search(
        self, tenant_id: str, query: str, k: int = 3, min_score: float = -1.0
    ) -> list[Chunk]:
        store = self._stores.get(tenant_id)
        return store.search(query, k, min_score) if store else []
