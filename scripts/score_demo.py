from datetime import date
from pathlib import Path

from src.ingestion import make_chunks
from src.sbert_embedder import MiniLMEmbedder

QUESTIONS = [
    "How many days of annual leave do I get?",
    "Can I work from home?",
    "How do I claim expenses?",
    "When is salary paid?",
    "Where can I park my car?",
    "What is the capital of France?",
    "Who won the football match?",
]

embedder = MiniLMEmbedder()
chunks = make_chunks(
    Path("samples/hr_policy.txt"), "policy", "1.0", date(2026, 1, 1), size=40, overlap=10
)
chunk_vectors = embedder.embed([c.text for c in chunks])

for question in QUESTIONS:
    scores = chunk_vectors @ embedder.embed([question])[0]
    best = scores.argmax()
    print(f"{scores[best]:.2f}  {question}  ->  {chunks[best].text[:45]}")
