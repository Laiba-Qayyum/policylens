from datetime import date
from pathlib import Path

from src.ingestion import make_chunks
from src.tenants import TenantStores


def ingest_files(
    stores: TenantStores,
    tenant_id: str,
    paths: list[Path],
    doc_type: str = "policy",
    version: str = "1.0",
) -> int:
    """Load each file into the tenant's store. Returns the number of chunks added."""
    added = 0
    for path in paths:
        doc_date = date.fromtimestamp(path.stat().st_mtime)
        chunks = make_chunks(path, doc_type, version, doc_date)
        stores.add(tenant_id, chunks)
        added += len(chunks)
    return added
