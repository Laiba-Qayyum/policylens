from datetime import date
from pathlib import Path

from src.evaluation import Case, evaluate
from src.faiss_store import FaissStore
from src.ingestion import make_chunks
from src.sbert_embedder import MiniLMEmbedder

CASES = [
    Case("How many days of annual leave do I get?", "20 days"),
    Case("How far in advance must I request leave?", "one week"),
    Case("Can I carry over unused leave?", "five days"),
    Case("When are salaries paid?", "last working day"),
    Case("How often can I work remotely?", "two days per week"),
    Case("What is the deadline for expense claims?", "thirty days"),
    Case("Do I need receipts for expenses?", "receipts"),
    Case("Where can I park my car?", None),
    Case("What is the capital of France?", None),
    Case("Who won the football match?", None),
    Case("What health insurance does the company offer?", None),
]
CUTOFFS = [-1.0, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5]

embedder = MiniLMEmbedder()
store = FaissStore(embedder, embedder.dim)
store.add(
    make_chunks(
        Path("samples/hr_policy.txt"), "policy", "1.0", date(2026, 1, 1), size=40, overlap=10
    )
)

answerable = [c for c in CASES if c.expected]
refusals = [c for c in CASES if not c.expected]

print("cutoff  answered  refused")
for cutoff in CUTOFFS:
    a, a_total = evaluate(store, answerable, k=1, min_score=cutoff)
    r, r_total = evaluate(store, refusals, k=1, min_score=cutoff)
    print(f"{cutoff:>6}  {a}/{a_total}       {r}/{r_total}")
