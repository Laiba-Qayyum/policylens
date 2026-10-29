from dataclasses import dataclass, field

from src.citations import cited_sources
from src.conflicts import find_competing_sources
from src.ingestion import Chunk
from src.llm import LLM
from src.prompts import build_prompt
from src.tenants import TenantStores

REFUSAL = "I don't know."


@dataclass(frozen=True)
class Answer:
    text: str
    sources: list[Chunk]
    competing: list[str] = field(default_factory=list)
    verified: bool = True


def answer_question(
    tenant_id: str,
    question: str,
    stores: TenantStores,
    llm: LLM,
    k: int = 3,
    min_score: float = -1.0,
) -> Answer:
    chunks = stores.search(tenant_id, question, k, min_score)
    if not chunks:
        return Answer(REFUSAL, [])
    reply = llm.complete(build_prompt(question, chunks))
    if reply.strip().lower().startswith("i don't know"):
        return Answer(REFUSAL, [])
    cited, invalid = cited_sources(reply, chunks)
    verified = bool(cited) and not invalid
    return Answer(reply, cited or chunks, find_competing_sources(chunks), verified)
