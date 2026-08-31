FROM python:3.11-slim

WORKDIR /app

# Install system deps for simulators
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && rm -rf /var/lib/apt/lists/*

# Copy poetry files
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copy source
COPY src/ ./src/
COPY .env ./

EXPOSE 8000

CMD ["uvicorn", "src.qcc.main:app", "--host", "0.0.0.0", "--port", "8000"]
