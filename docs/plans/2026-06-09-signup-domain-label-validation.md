# Signup Domain Label Validation Plan

status: completed

## Context

NextInvite normalizes signup emails, checks broad email shape, caps addresses at
254 characters, and rejects unsafe dot placement. Domain labels with
leading/trailing hyphens or labels longer than 63 characters could still pass
before datastore persistence.

## Objectives

- Reject domain labels that start or end with a hyphen.
- Reject domain labels longer than 63 characters.
- Preserve existing normalization, length, dot-placement, and deterministic 400
  behavior.
- Extend the SDK-free baseline so domain label validation remains covered.

## Verification

- `python3 scripts/check-baseline.py`
- `make check`
- `git diff --check`
