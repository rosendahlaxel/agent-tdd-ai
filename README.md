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

### Codex-assisted test fixing
Use the helper workflow to rerun tests and let Codex suggest focused fixes without weakening or deleting tests:
```bash
make codex-fix
# or
./scripts/codex-fix-tests.sh
```
The script runs `pytest`, feeds failing output to `codex edit`, and then reruns the suite to verify the proposed changes.

### CI: tests with optional Codex auto-fix
- Workflow: `.github/workflows/test-and-codex.yml` runs only via manual dispatch from GitHub Actions. Set input `run_codex=true` to opt in. On failing tests, it uses the official `openai/codex-action@v1` with prompt `.github/codex/prompts/fix-tests.md`, uploads `codex-fix.patch` and `codex-output.md`, and commits/pushes fixes back to the checked-out branch when the rerun passes.
- Secrets: add `OPENAI_API_KEY` in repository secrets. Without a token, the Codex step is skipped and the workflow fails to surface the test failure.
- Artifacts: the workflow uploads Codex’s final message (`codex-output.md`) and the patch (`codex-fix.patch`) for review.

#### Requirements and CI usage
- For local runs, install and authenticate the `codex` CLI (expects `OPENAI_API_KEY` or `CODEX_API_KEY`).
- For CI, store `OPENAI_API_KEY` as a repository secret; the workflow uses the official Codex GitHub Action and only runs when dispatched manually with `run_codex=true`.

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
