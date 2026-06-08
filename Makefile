.PHONY: check verify static-check

PYTHON ?= python3

check: verify

verify: static-check

static-check:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) scripts/check-baseline.py
