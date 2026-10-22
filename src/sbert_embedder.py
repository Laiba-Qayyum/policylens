import numpy as np
from sentence_transformers import SentenceTransformer


class MiniLMEmbedder:
    dim = 384

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> np.ndarray:
        return self._model.encode(texts, normalize_embeddings=True).astype("float32")
