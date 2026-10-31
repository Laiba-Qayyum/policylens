import os
from pathlib import Path

from src.api import create_app
from src.faiss_store import FaissStore
from src.ollama_llm import OllamaLLM
from src.sbert_embedder import MiniLMEmbedder
from src.tenants import TenantStores

embedder = MiniLMEmbedder()
data_dir = Path(os.environ.get("POLICYLENS_DATA", "data/tenants"))
stores = TenantStores(lambda: FaissStore(embedder, MiniLMEmbedder.dim), directory=data_dir)
app = create_app(stores, OllamaLLM())
