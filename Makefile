.PHONY: setup lint test run-enhance run-audio run-listen

setup:
	python -m pip install --upgrade pip
	pip install -e '.[api,ui]'
	@if [ -f .pre-commit-config.yaml ]; then \
		pip install pre-commit && pre-commit install; \
		else echo "(pre-commit not configured)"; fi

lint:
	@command -v ruff >/dev/null 2>&1 && ruff . || echo "(ruff not installed)"
	@command -v black >/dev/null 2>&1 && black --check . || echo "(black not installed)"

test:
	pytest -q

run-enhance:
	@TEXT?=Sample enhancement from Makefile
	python -m lazy_ptt.cli --verbose enhance-text --text "$(TEXT)" ${AUTO_MOVE}

run-audio:
	@if [ -z "$(AUDIO)" ]; then echo "Set AUDIO=/path/to/file.wav"; exit 1; fi
	python -m lazy_ptt.cli --verbose process-audio "$(AUDIO)" ${AUTO_MOVE}

run-listen:
	python -m lazy_ptt.cli --verbose listen ${AUTO_MOVE}

