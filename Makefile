ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell path='$(subst ','"'"',$(MAKEFILE_LIST))'; path=$$(printf '%s' "$$path" | /usr/bin/sed 's/^ //'); /usr/bin/dirname -- "$$path")

.PHONY: build check lint static-check test verify

PYTHON ?= python3

check: verify

verify: static-check

lint test build: static-check

static-check:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/check-baseline.py"
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -W ignore::DeprecationWarning "$(ROOT)/tests/test_debug_trace_policy.py"
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/tests/test_vendored_tornado_surface.py"
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/tests/test_makefile_root.py"
