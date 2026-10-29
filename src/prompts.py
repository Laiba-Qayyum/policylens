from src.conflicts import find_competing_sources
from src.ingestion import Chunk


def build_prompt(question: str, chunks: list[Chunk]) -> str:
    sources = "\n".join(
        f"[{n}] {c.source}, page {c.page}: {c.text} (version {c.version}, dated {c.doc_date})"
        for n, c in enumerate(chunks, start=1)
    )
    rules = "Answer the question using only the sources below. Cite the sources you use like [1]. "
    if find_competing_sources(chunks):
        rules += (
            "If sources disagree, do not refuse: answer with the newest one and say that "
            "an older source differs. "
            "Only if no source is relevant to the question, reply exactly: I don't know."
        )
    else:
        rules += "If the sources do not contain the answer, reply exactly: I don't know."
    return f"{rules}\n\nSources:\n{sources}\n\nQuestion: {question}\nAnswer:"
