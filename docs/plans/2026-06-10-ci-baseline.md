# CI Baseline

status: completed

## Context

The portfolio remediation plan calls for lightweight CI on high-priority repos
with passing local checks. NextInvite is a legacy App Engine sample, but its
current baseline runs dependency-free under Python 3 with App Engine and Tornado
stubs.

## Completed Scope

- Added a GitHub Actions workflow for pushes, pull requests, and manual runs.
- Configured CI to run `make check`, which delegates to
  `scripts/check-baseline.py`.
- Extended the static baseline and docs so the CI gate remains visible.

## Verification

- `make check`
- `git diff --check`
