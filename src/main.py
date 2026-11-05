import os
from pathlib import Path

from src.activity import ActivityLog
from src.api import create_app
from src.faiss_store import FaissStore
from src.keys import parse_api_keys
from src.ollama_llm import OllamaLLM
from src.registry import TenantRegistry
from src.sbert_embedder import MiniLMEmbedder
from src.tenants import TenantStores

raw_keys = os.environ.get("POLICYLENS_KEYS", "")
try:
    api_keys = parse_api_keys(raw_keys) if raw_keys.strip() else {}
except ValueError as error:
    raise SystemExit(
        f"POLICYLENS_KEYS is invalid: {error}. "
        "Set it like acme:<a key of at least 16 characters>, separating tenants with commas, "
        "or leave it unset and create workspaces from the sign-up page."
    ) from error

embedder = MiniLMEmbedder()
data_dir = Path(os.environ.get("POLICYLENS_DATA", "data/tenants"))
stores = TenantStores(lambda: FaissStore(embedder, MiniLMEmbedder.dim), directory=data_dir)
activity = ActivityLog(data_dir / "activity")
registry = TenantRegistry(data_dir / "auth")
ollama_url = os.environ.get("OLLAMA_URL")
llm = OllamaLLM(url=ollama_url) if ollama_url else OllamaLLM()
app = create_app(stores, llm, api_keys=api_keys, activity=activity, registry=registry)
