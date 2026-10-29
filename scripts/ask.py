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
    ingest_files(stores, args.tenant, args.files)

    answer = answer_question(
        args.tenant, args.question, stores, OllamaLLM(), min_score=args.min_score
    )
    print(answer.text)
    for n, chunk in enumerate(answer.sources, start=1):
        print(f"  [{n}] {chunk.source}, page {chunk.page}")
    if answer.competing:
        print(f"Note: these files may disagree (newest first): {', '.join(answer.competing)}")


if __name__ == "__main__":
    main(sys.argv[1:])
