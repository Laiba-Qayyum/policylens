FROM python:3.11.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POLICYLENS_DATA=/data

WORKDIR /app

# CPU-only PyTorch first, so sentence-transformers does not pull the large GPU build.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install dependencies before the code so Docker can cache this layer.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/

RUN useradd --create-home appuser && mkdir /data && chown appuser /data
USER appuser

# Download the embedding model at build time, so starting the container needs no internet.
RUN python -c "from src.sbert_embedder import MiniLMEmbedder; MiniLMEmbedder()"

VOLUME /data
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]