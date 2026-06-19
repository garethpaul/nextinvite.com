ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: build check lint static-check test verify

PYTHON ?= python3

check: verify

verify: static-check

lint test build: static-check

static-check:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/check-baseline.py"
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -W ignore::DeprecationWarning "$(ROOT)/tests/test_debug_trace_policy.py"
