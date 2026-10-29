import sys

from src.answering import answer_question
from src.cli import parse_args
from src.faiss_store import FaissStore
from src.ollama_llm import OllamaLLM
from src.pipeline import ingest_files
from src.sbert_embedder import MiniLMEmbedder
from src.tenants import TenantStores


def main(argv: list[str]) -> None:
    args = parse_args(argv)
    embedder = MiniLMEmbedder()
    stores = TenantStores(lambda: FaissStore(embedder, MiniLMEmbedder.dim))
    ingest_files(stores, args.tenant, args.files, doc_dates=args.dates)
    answer = answer_question(
        args.tenant, args.question, stores, OllamaLLM(), min_score=args.min_score
    )
    print(answer.text)
    for chunk in answer.sources:
        print(f"  source: {chunk.source}, page {chunk.page}")
    if not answer.verified:
        print("Warning: unverified. The reply did not cite a valid source.")
    if answer.competing:
        print(f"Note: these files may disagree (newest first): {', '.join(answer.competing)}")


if __name__ == "__main__":
    main(sys.argv[1:])
