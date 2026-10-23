from dataclasses import dataclass

from src.ingestion import Chunk
from src.llm import LLM
from src.prompts import build_prompt
from src.tenants import TenantStores


@dataclass(frozen=True)
class Answer:
    text: str
    sources: list[Chunk]


def answer_question(
    tenant_id: str, question: str, stores: TenantStores, llm: LLM, k: int = 3
) -> Answer:
    chunks = stores.search(tenant_id, question, k)
    if not chunks:
        return Answer("I don't know.", [])
    return Answer(llm.complete(build_prompt(question, chunks)), chunks)
