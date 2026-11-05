import secrets
import tempfile
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, UploadFile
from pydantic import BaseModel

from src.answering import answer_question
from src.cli import DEFAULT_MIN_SCORE
from src.llm import LLM
from src.pipeline import ingest_files
from src.tenants import TenantStores


class AskRequest(BaseModel):
    question: str


def create_app(
    stores: TenantStores,
    llm: LLM,
    min_score: float = DEFAULT_MIN_SCORE,
    api_keys: dict[str, str] | None = None,
) -> FastAPI:
    app = FastAPI(title="PolicyLens")

    def require_key(tenant_id: str, x_api_key: str | None = Header(default=None)) -> None:
        if api_keys is None:
            return
        expected = api_keys.get(tenant_id)
        if (
            expected is None
            or x_api_key is None
            or not secrets.compare_digest(x_api_key.encode(), expected.encode())
        ):
            raise HTTPException(status_code=401, detail="Invalid or missing API key")

    @app.post("/tenants/{tenant_id}/documents", dependencies=[Depends(require_key)])
    def upload(tenant_id: str, files: list[UploadFile]) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as folder:
            paths = []
            for upload_file in files:
                path = Path(folder) / Path(upload_file.filename or "upload").name
                path.write_bytes(upload_file.file.read())
                paths.append(path)
            try:
                chunks = ingest_files(stores, tenant_id, paths)
            except ValueError as error:
                raise HTTPException(status_code=400, detail=str(error)) from error
        return {"files": [path.name for path in paths], "chunks": chunks}

    @app.post("/tenants/{tenant_id}/ask", dependencies=[Depends(require_key)])
    def ask(tenant_id: str, request: AskRequest) -> dict[str, object]:
        answer = answer_question(tenant_id, request.question, stores, llm, min_score=min_score)
        return {
            "answer": answer.text,
            "sources": [{"source": c.source, "page": c.page} for c in answer.sources],
            "competing": answer.competing,
            "verified": answer.verified,
        }

    return app
