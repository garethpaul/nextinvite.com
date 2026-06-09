# Signup Top-Level Domain Validation

status: completed

## Context

Signup emails are normalized and validated before datastore writes, including
length, dot placement, local-part characters, and domain label syntax. The final
domain label still accepted one-character or all-numeric values that are weak
signup evidence for a public invite form.

## Objectives

- Reject one-character top-level domain labels.
- Reject all-numeric top-level domain labels.
- Preserve valid ASCII and punycode-style final labels with alphabetic content.
- Extend the SDK-free baseline and docs for top-level domain validation.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
