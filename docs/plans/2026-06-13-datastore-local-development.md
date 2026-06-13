---
title: Document datastore and local development boundaries
status: planned
date: 2026-06-13
---

# Document Datastore And Local Development Boundaries

## Goal

Make the preserved App Engine datastore model and historical local-development
requirements explicit without changing signup, persistence, deployment, or
vendored dependency behavior.

## Decisions

- Document `SignUp` as the only application datastore entity in the maintained
  source, with a normalized plaintext email, automatic creation timestamp, and
  deterministic `signup-<sha256>` key name.
- State that deterministic key hashing provides idempotency, not encryption or
  resistance to guessing known email addresses.
- Describe the runtime as the retired Python 2 App Engine standard environment
  with bundled `google.appengine` APIs and vendored Tornado modules.
- Treat `dev_appserver.py next/app.yaml` and classic `appcfg.py` deployment as
  historical workflows that require an era-compatible SDK, owned project, and
  explicit credential review; do not claim they were executed.
- Keep local datastore files, exports, credentials, and production user data
  outside version control.

## Implementation Units

### Root developer documentation

Files: `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`

- Add root-level local-development, datastore, and deployment-boundary notes.
- Explain the request path from `/signup` validation through deterministic
  datastore persistence.
- Align privacy guidance with the fact that normalized email remains stored as
  plaintext entity data.

### Regression contract

Files: `scripts/check-baseline.py`

- Require the README to name the entity, fields, key semantics, historical SDK
  commands, and non-verified deployment boundary.
- Require security and vision docs to retain plaintext-email, idempotency-only,
  local datastore/export, and credential ownership warnings.
- Require this plan to record completed status and actual verification before
  the full gate can pass.

## Verification

- Run `make lint`, `make test`, `make build`, and `make check`.
- Run the checker from an external working directory.
- Compile Python, parse App Engine and workflow YAML, and run
  `git diff --check`.
- Exercise hostile mutations that remove or weaken entity, plaintext-storage,
  historical-toolchain, deployment-ownership, and local-data exclusions.
- Scan only intended paths for credentials and generated artifacts.

## Risks

- Historical commands can be mistaken for supported deployment instructions;
  every command must be labeled unverified and tied to an era-compatible SDK.
- Hash-derived keys can be mistaken for encrypted email storage; documentation
  must state that the entity still stores normalized email in plaintext.
