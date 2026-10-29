from fastapi import FastAPI
from pydantic import BaseModel

from src.answering import answer_question
from src.cli import DEFAULT_MIN_SCORE
from src.llm import LLM
from src.tenants import TenantStores


class AskRequest(BaseModel):
    question: str


def create_app(stores: TenantStores, llm: LLM, min_score: float = DEFAULT_MIN_SCORE) -> FastAPI:
    app = FastAPI(title="PolicyLens")

    @app.post("/tenants/{tenant_id}/ask")
    def ask(tenant_id: str, request: AskRequest) -> dict[str, object]:
        answer = answer_question(tenant_id, request.question, stores, llm, min_score=min_score)
        return {
            "answer": answer.text,
            "sources": [{"source": c.source, "page": c.page} for c in answer.sources],
            "competing": answer.competing,
        }

    return app
