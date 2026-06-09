# Signup Domain Label Character Plan

status: completed

## Context

Signup email validation already normalizes addresses, caps total length, rejects
unsafe dot placement, and checks domain label length and hyphen boundaries.
However, labels containing underscores or non-ASCII characters still passed the
legacy format regex and could be stored in the datastore.

## Objectives

- Restrict domain labels to ASCII letters, digits, and interior hyphens.
- Keep interior hyphen labels accepted.
- Reject underscore and non-ASCII domain label examples before datastore writes.
- Extend the SDK-free baseline checker and docs for the domain label character
  validation boundary.

## Verification

- `make check`
- `git diff --check`
