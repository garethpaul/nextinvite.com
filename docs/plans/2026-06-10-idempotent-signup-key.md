# Idempotent Signup Key

status: completed

## Problem

Each valid signup currently creates a new datastore entity, so retries and
case/whitespace variants of the same normalized address can create duplicates.
Using the raw address as a key would avoid duplicates but expose personal data
in datastore identifiers.

## Scope

- Derive a deterministic SHA-256 key from the normalized email address.
- Prefix the digest so signup keys remain identifiable without containing the
  address itself.
- Construct `SignUp` with the deterministic key before persistence.
- Add dependency-free checks for normalization equivalence and plaintext
  exclusion.
- Document idempotency and the privacy boundary without claiming encryption.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- mutation checks for normalization and hashed-key persistence
- `git diff --check`

## Work Completed

- Added `signup_key_name` using the normalized UTF-8 email and SHA-256.
- Prefixed datastore identifiers with `signup-` while excluding plaintext email.
- Constructed `SignUp` with the deterministic key so retries target one entity.
- Added dependency-free checks for case/whitespace equivalence, key shape, and
  plaintext exclusion.
- Documented that deterministic hashing supports idempotency but is not encryption.
