#!/usr/bin/env bash
set -euo pipefail

# Ensure Codex CLI is available before continuing so the workflow fails fast in CI
# or on fresh machines.
if ! command -v codex >/dev/null 2>&1; then
  echo "codex CLI not found. Install and authenticate it before running this script." >&2
  exit 1
fi

# Require an API token so Codex can reach the service. The CLI typically respects
# OPENAI_API_KEY (or CODEX_API_KEY, depending on local setup), so check for either
# to help users catch configuration issues early.
if [[ -z "${OPENAI_API_KEY:-}" && -z "${CODEX_API_KEY:-}" ]]; then
  echo "Codex authentication token not found. Set OPENAI_API_KEY or CODEX_API_KEY before running." >&2
  exit 1
fi

# Temporary file to capture pytest output.
PYTEST_LOG="/tmp/pytest.log"

# Run pytest and tee output to the log file. Using the command in an if-statement
# prevents immediate exit on failure when 'set -e' is enabled.
if pytest | tee "${PYTEST_LOG}"; then
  echo "All tests passed, no Codex fix needed."
  exit 0
fi

# If pytest failed, attempt to have Codex automatically fix the code.
echo "Tests failed, invoking Codex to attempt an automated fix..."

# Run codex edit with the relevant source, tests, and configuration files.
# Pytest output is provided via stdin so Codex can understand the failure.
codex edit \
  app/**/*.py \
  tests/**/*.py \
  pyproject.toml \
  --instruction "Tests are failing. Read the pytest output provided on stdin and update the implementation so that all tests pass without weakening, deleting, or skipping any tests. Do not comment out tests. Use idiomatic FastAPI, respect the existing design, and keep the code compatible with Ruff (lint and formatting). Prefer minimal, focused changes." \
  < "${PYTEST_LOG}"

echo "Codex edit completed. Re-running pytest..."

# Re-run pytest to verify whether Codex resolved the failures.
if pytest; then
  echo "Tests passed after Codex edit."
  exit 0
fi

# If tests are still failing, exit non-zero to signal manual intervention is needed.
echo "Tests are still failing after Codex edit. Manual intervention required."
exit 1
