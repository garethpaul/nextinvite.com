# Signup Email Dot Validation Plan

status: completed

## Context

Signup emails were normalized, format-checked, and capped at the 254-character address boundary. Dot placement edge cases such as leading, trailing, or consecutive dots could still pass the broad shape check.

## Objectives

- Reject leading-dot and trailing-dot local parts.
- Reject consecutive dots in local or domain portions.
- Preserve existing normalization, length, and deterministic 400 behavior.
- Extend the static baseline and docs to preserve email dot validation.

## Verification

- `python3 scripts/check-baseline.py`
- `make check`
- `git diff --check`
