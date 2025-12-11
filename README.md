# FastAPI TDD Demo Service

A simple FastAPI web API that demonstrates test-driven development, linting with Ruff, and containerization with Docker.

## Features
- **Health check:** `GET /health` returns `{ "status": "ok" }`.
- **In-memory items:**
  - `POST /items` to create an item with a unique ID (name must be at least 3 characters).
  - `GET /items/{item_id}` to fetch a specific item.
  - `GET /items` to list all items.

## Getting Started

### Installation
```bash
pip install -e '.[dev]'
```

### Run the API locally
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Visit http://localhost:8000/health to confirm the service is running.

### Tests (TDD workflow)
```bash
pytest
```

### Linting and Formatting
```bash
ruff check
ruff format
```

## Docker
Build the image:
```bash
docker build -t agent-tdd-ai .
```

Run the container:
```bash
docker run --rm -p 8000:8000 agent-tdd-ai
```

## docker-compose (optional)
For convenience, a `docker-compose.yml` file is provided:
```bash
docker-compose up --build
```
This exposes the API on port 8000.
