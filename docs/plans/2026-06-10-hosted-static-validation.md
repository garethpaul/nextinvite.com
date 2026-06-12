# Hosted Static Validation

status: completed

## Context

The repository has dependency-free checks for signup normalization, templates,
App Engine configuration, XSRF-aware form submission, and vendored boundaries,
but no hosted validation.

## Priorities

1. Run the canonical SDK-free `make check` gate on hosted Linux.
2. Pin checkout, Python, permissions, runner, timeout, and concurrency behavior.
3. Enforce the workflow contract from `scripts/check-baseline.py`.
4. Keep App Engine deployment, datastore access, and external services outside CI.

## Implementation Units

Files:

- `.github/workflows/check.yml`
- `scripts/check-baseline.py`
- `README.md`
- `VISION.md`
- `SECURITY.md`
- `CHANGES.md`

Add push, pull-request, and manual triggers; read-only permissions; concurrency
cancellation; a bounded `ubuntu-24.04` job; commit-pinned checkout and Python
setup; and `make check`. Require that contract from the baseline checker.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- workflow YAML parse
- `git diff --check`
- successful hosted Linux `Check` workflow for the pushed commit

## Boundaries

- Do not deploy App Engine or access a datastore in CI.
- Do not contact external services or add runtime dependencies.
