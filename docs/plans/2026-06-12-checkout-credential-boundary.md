# Checkout Credential Boundary

status: completed

## Context

The recorded baseline describes hosted checkout as credential-free, but the
exact PR head still uses the checkout action's default credential persistence.
The Linux job only needs repository contents for dependency-free static checks.

## Objectives

- Disable checkout credential persistence without changing signup behavior.
- Enforce one workflow, one read-only permission block, one checkout action,
  and one correctly nested non-persisted credential declaration.
- Preserve immutable action pins, Python 3.12, Ubuntu 24.04, timeout,
  concurrency, and `make check`.
- Correct documentation to match the exact workflow.

## Implementation Units

### Workflow And Checker

Files: `.github/workflows/check.yml` and `scripts/check-baseline.py`.

Add the checkout boundary and reject duplicate workflows, permissions,
checkout actions, write scopes, misplaced or contradictory settings, and
incomplete plan evidence.

### Documentation

Files: `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`, and this plan.

Record the shorter credential lifetime while preserving the dependency-free
hosted boundary.

## Work Completed

- Added `persist-credentials: false` beneath the sole pinned checkout step.
- Added exact workflow, permission, checkout, nesting, contradiction, and plan
  evidence contracts to `scripts/check-baseline.py`.
- Updated hosted-validation documentation without changing application code,
  App Engine configuration, or dependencies.

## Verification Completed

- `python3 scripts/check-baseline.py`
- `make lint`, `make test`, `make build`, and `make check`
- workflow YAML parse and `git diff --check`
- Hostile workflow and plan mutations

The local checks remain dependency-free and do not deploy App Engine, access
datastore, or exercise live signup requests. Canonical hosted push and
pull-request checks remain required at the exact successor head before owner
merge.

## Boundaries

- Do not change server code, templates, JavaScript, CSS, App Engine files, or
  tests.
- Do not deploy, access datastore, or exercise live signup requests.
- Preserve the existing remediation PR and evidence.
