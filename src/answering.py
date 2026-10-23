from dataclasses import dataclass

from src.ingestion import Chunk
from src.llm import LLM
from src.prompts import build_prompt
from src.tenants import TenantStores

REFUSAL = "I don't know."


@dataclass(frozen=True)
class Answer:
    text: str
    sources: list[Chunk]


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
    return Answer(reply, chunks)
