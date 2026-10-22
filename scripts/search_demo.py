from datetime import date
from pathlib import Path

from src.faiss_store import FaissStore
from src.ingestion import make_chunks
from src.sbert_embedder import MiniLMEmbedder
from src.tenants import TenantStores

embedder = MiniLMEmbedder()
stores = TenantStores(lambda: FaissStore(embedder, MiniLMEmbedder.dim))

chunks = make_chunks(
    Path("samples/hr_policy.txt"), "policy", "1.0", date(2026, 1, 1), size=20, overlap=5
)
stores.add("acme", chunks)

for chunk in stores.search("acme", "How many vacation days do I get?", k=2):
    print(f"[{chunk.source} p{chunk.page}] {chunk.text}\n")
