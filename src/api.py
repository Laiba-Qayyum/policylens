import secrets
import tempfile
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Response, UploadFile
from pydantic import BaseModel

from src.activity import ActivityLog
from src.answering import answer_question
from src.cli import DEFAULT_MIN_SCORE
from src.llm import LLM
from src.pipeline import ingest_files
from src.registry import TenantRegistry
from src.tenants import TenantStores


class AskRequest(BaseModel):
    question: str


class WorkspaceRequest(BaseModel):
    name: str


def create_app(
    stores: TenantStores,
    llm: LLM,
    min_score: float = DEFAULT_MIN_SCORE,
    api_keys: dict[str, str] | None = None,
    activity: ActivityLog | None = None,
    registry: TenantRegistry | None = None,
) -> FastAPI:
    app = FastAPI(title="PolicyLens")
    log = activity if activity is not None else ActivityLog()
    configured = api_keys or {}

    def key_is_valid(tenant_id: str, given: str) -> bool:
        expected = configured.get(tenant_id)
        from_settings = expected is not None and secrets.compare_digest(
            given.encode(), expected.encode()
        )
        from_registry = registry is not None and registry.check(tenant_id, given)
        return from_settings or from_registry

    def require_key(tenant_id: str, x_api_key: str | None = Header(default=None)) -> None:
        if api_keys is None and registry is None:
            return
        if x_api_key is None or not key_is_valid(tenant_id, x_api_key):
            raise HTTPException(status_code=401, detail="Invalid or missing API key")

    @app.post("/tenants")
    def create_workspace(request: WorkspaceRequest, response: Response) -> dict[str, str]:
        if registry is None:
            raise HTTPException(status_code=404, detail="Workspace sign-up is not enabled")
        name = request.name
        taken = name in configured or registry.exists(name) or stores.documents(name)
        if taken:
            raise HTTPException(status_code=409, detail="That workspace name is already taken")
        try:
            key = registry.create(name)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        except FileExistsError as error:
            raise HTTPException(
                status_code=409, detail="That workspace name is already taken"
            ) from error
        response.headers["Cache-Control"] = "no-store"
        return {"tenant": name, "api_key": key}

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
        for path in paths:
            log.record(tenant_id, "upload", path.name)
        return {"files": [path.name for path in paths], "chunks": chunks}

    @app.get("/tenants/{tenant_id}/documents", dependencies=[Depends(require_key)])
    def list_documents(tenant_id: str) -> dict[str, object]:
        documents = stores.documents(tenant_id)
        return {
            "documents": documents,
            "total_chunks": sum(d["chunks"] for d in documents),
        }

    @app.get("/tenants/{tenant_id}/activity", dependencies=[Depends(require_key)])
    def get_activity(tenant_id: str) -> dict[str, object]:
        return {"events": log.recent(tenant_id), "summary": log.summary(tenant_id)}

    @app.post("/tenants/{tenant_id}/ask", dependencies=[Depends(require_key)])
    def ask(tenant_id: str, request: AskRequest) -> dict[str, object]:
        answer = answer_question(tenant_id, request.question, stores, llm, min_score=min_score)
        log.record(tenant_id, "question", verified=answer.verified and bool(answer.sources))
        return {
            "answer": answer.text,
            "sources": [{"source": c.source, "page": c.page} for c in answer.sources],
            "competing": answer.competing,
            "verified": answer.verified,
        }

    return app
