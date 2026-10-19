FROM python:3.11.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first so Docker can cache this layer when only code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/

RUN useradd --create-home appuser
USER appuser

# Placeholder until the API exists (Day 8): check that settings load.
CMD ["python", "-c", "from src.config import Settings; Settings(); print('PolicyLens image OK')"]
