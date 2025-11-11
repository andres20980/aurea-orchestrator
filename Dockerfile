FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
COPY aurea_orchestrator ./aurea_orchestrator

RUN pip install --no-cache-dir -e .

CMD ["python", "-m", "aurea_orchestrator"]
