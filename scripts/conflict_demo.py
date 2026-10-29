from datetime import date
from pathlib import Path

from src.answering import answer_question
from src.faiss_store import FaissStore
from src.ingestion import make_chunks
from src.ollama_llm import OllamaLLM
from src.sbert_embedder import MiniLMEmbedder
from src.tenants import TenantStores

FILES = [
    ("returns_2025.txt", "1.0", date(2025, 1, 1)),
    ("returns_2026.txt", "2.0", date(2026, 1, 1)),
]

embedder = MiniLMEmbedder()
stores = TenantStores(lambda: FaissStore(embedder, MiniLMEmbedder.dim))
for name, version, day in FILES:
    chunks = make_chunks(Path("samples") / name, "policy", version, day, size=40, overlap=10)
    stores.add("acme", chunks)

question = "How many days do I have to return an item?"
answer = answer_question("acme", question, stores, OllamaLLM(), min_score=0.15)

print(f"A: {answer.text}")
for chunk in answer.sources:
    print(f"  source: {chunk.source} (v{chunk.version}, {chunk.doc_date})")
print(f"Competing, newest first: {answer.competing}")
