from src.api import create_app
from src.faiss_store import FaissStore
from src.ollama_llm import OllamaLLM
from src.sbert_embedder import MiniLMEmbedder
from src.tenants import TenantStores

embedder = MiniLMEmbedder()
stores = TenantStores(lambda: FaissStore(embedder, MiniLMEmbedder.dim))
app = create_app(stores, OllamaLLM())
