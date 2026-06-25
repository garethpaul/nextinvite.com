# Transactional Signup Insert

## Status: Completed

## Context

Signup retries used a deterministic datastore key but constructed and put a new
`SignUp` model each time. Legacy App Engine datastore writes overwrite an
existing entity with the same key, so the implementation did not preserve the
first entity or its automatic creation timestamp as the documentation claimed.

## Design

Centralize persistence in `persist_signup()` and use the legacy `db.Model`
`get_or_insert()` class method with the existing normalized SHA-256 key. The API
transactionally retrieves the existing entity or creates it with the normalized
email, discarding later constructor values when the key already exists.

A manual read followed by `put()` was rejected because concurrent retries could
race. Keeping the existing constructor/put sequence was rejected because it
overwrites the complete entity for every retry.

## Work Completed

- Added a transactional get-or-insert persistence helper.
- Routed the signup handler through that helper.
- Added a dependency-free fake-model regression proving normalized retries
  return and retain the first entity.
- Tightened the static contract against fresh deterministic-key overwrites.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 tests/test_signup_persistence.py`
- `/usr/bin/make check`
- `git diff --check`

## App Engine Evidence

- Legacy DB `get_or_insert()` transactionally guarantees uniqueness and returns
  the existing entity on later calls:
  https://docs.cloud.google.com/appengine/docs/legacy/standard/python/refdocs/google.appengine.ext.db
- A normal `put()` with an existing key overwrites the complete entity:
  https://docs.cloud.google.com/appengine/docs/legacy/standard/python/datastore/entities

## Scope Boundaries

- Email normalization, validation, XSRF handling, request-size limits, key
  derivation, response text, and stored plaintext email are unchanged.
- No live App Engine SDK, datastore, deployment, or private signup data was used.
