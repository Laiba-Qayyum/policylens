from src.ingestion import Chunk


def build_prompt(question: str, chunks: list[Chunk]) -> str:
    sources = "\n".join(
        f"[{n}] {c.source}, page {c.page}: {c.text}" for n, c in enumerate(chunks, start=1)
    )
    return (
        "Answer the question using only the sources below. "
        "Cite the sources you use like [1]. "
        "If the sources do not contain the answer, reply exactly: I don't know.\n\n"
        f"Sources:\n{sources}\n\n"
        f"Question: {question}\n"
        "Answer:"
    )
