from datetime import date
from pathlib import Path

from src.answering import answer_question
from src.faiss_store import FaissStore
from src.ingestion import make_chunks
from src.ollama_llm import OllamaLLM
from src.sbert_embedder import MiniLMEmbedder
from src.tenants import TenantStores

MIN_SCORE = 0.15  # chosen from scripts/eval_cutoffs.py on a small sample

embedder = MiniLMEmbedder()
stores = TenantStores(lambda: FaissStore(embedder, MiniLMEmbedder.dim))
chunks = make_chunks(
    Path("samples/hr_policy.txt"), "policy", "1.0", date(2026, 1, 1), size=40, overlap=10
)
stores.add("acme", chunks)
llm = OllamaLLM()

for question in ["How many days of annual leave do I get?", "What is the parking policy?"]:
    answer = answer_question("acme", question, stores, llm, min_score=MIN_SCORE)
    print(f"Q: {question}\nA: {answer.text}")
    for n, chunk in enumerate(answer.sources, start=1):
        print(f"  [{n}] {chunk.source}, page {chunk.page}")
    print()
