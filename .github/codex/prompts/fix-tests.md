You are an expert FastAPI engineer. Tests have failed in CI. Use the pytest output at /tmp/pytest.log to understand the failures, then update the code so all tests in tests/test_api.py pass without weakening, deleting, or skipping any tests.

Constraints and context:
- Keep behavior in-memory and compatible with Python 3.12, FastAPI, and the existing Ruff settings.
- Prefer minimal, targeted changes that preserve the current API design.
- Important files: app/main.py, tests/test_api.py, pyproject.toml.
- After making changes, ensure the test expectations still make sense and rely on FastAPI idioms.
