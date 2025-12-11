.PHONY: test codex-fix

# Run the pytest suite.
test:
	pytest

# Run Codex-assisted test fixing workflow.
# Ensure scripts/codex-fix-tests.sh is executable (chmod +x scripts/codex-fix-tests.sh).
codex-fix:
	./scripts/codex-fix-tests.sh
