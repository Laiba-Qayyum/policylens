from datetime import date
from pathlib import Path

from src.ingestion import Chunk, make_chunks
from src.tenants import TenantStores


def ingest_files(
    stores: TenantStores,
    tenant_id: str,
    paths: list[Path],
    doc_type: str = "policy",
    version: str = "1.0",
) -> int:
    """Load every file, then add them all. If any file fails, nothing is added.

    Returns the number of chunks added.
    """
    loaded: list[list[Chunk]] = []
    for path in paths:
        doc_date = date.fromtimestamp(path.stat().st_mtime)
        loaded.append(make_chunks(path, doc_type, version, doc_date))
    for chunks in loaded:
        stores.add(tenant_id, chunks)
    return sum(len(chunks) for chunks in loaded)
