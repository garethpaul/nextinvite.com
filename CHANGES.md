# Changes

## 2026-06-25 - P2 - Harden fresh XSRF cookies

### Summary
Configured the signup application's fresh production XSRF cookie as `Secure`
and `HttpOnly` while preserving `HttpOnly`-only HTTP development cookies and
keeping the contained Tornado framework default opt-in.

### Work completed
- Added app-owned XSRF cookie keyword arguments to the WSGI subset.
- Added converted WSGI behavior coverage and six hostile source mutations.
- Documented HTTPS ownership and hidden-field compatibility.

### Validation
- The fresh-cookie WSGI assertion failed before implementation with only
  `_xsrf=<token>; Path=/`.
- `python3 tests/test_vendored_tornado_surface.py` passed after implementation.
- `/usr/bin/make check` and `git diff --check` passed.

### Bugs / findings
- P2: fresh XSRF tokens were sent without transport or script-access flags.

### Blockers
- No classic App Engine SDK or live Python 2 deployment was available.

### Next action
- Open a PR and complete Codex plus hosted review before merge.

## 2026-06-25 04:44 - P2 - Preserve the first signup entity

### Summary
Replaced overwrite-based deterministic signup writes with the legacy datastore's
transactional get-or-insert boundary so retries preserve original metadata.

### Work completed
- Added atomic normalized-email signup persistence with `get_or_insert()`.
- Added an offline retry regression that proves one entity is retained.

### Threads
- Started: none — work completed directly in the current repository.
- Continued: none.
- Stopped: none.

### Files changed
- `next/server.py` — added transactional signup persistence.
- `tests/test_signup_persistence.py` — added retry/idempotency coverage.
- `tests/test_vendored_tornado_surface.py` — exercised duplicate HTTP signup retries.
- `Makefile`, `scripts/check-baseline.py` — wired and enforced the new contract.
- Documentation and plan files — recorded behavior, evidence, and risks.

### Validation
- `python3 tests/test_signup_persistence.py` — passed after failing before implementation.
- `/usr/bin/make check` — passed all baseline, error-policy, persistence,
  converted WSGI smoke, and Make-root tests.
- `git diff --check` — passed.

### Bugs / findings
- P2: constructing and putting a fresh model for an existing deterministic key
  overwrote the entity instead of preserving the first signup record.

### Blockers
- Live legacy App Engine datastore validation is unavailable; offline contract
  tests and hosted CI cover the maintained surface.

### Next action
- Open a PR and complete Codex plus hosted review before merge.

## 2026-06-21

- Made absolute Makefile verification portable across checkout paths containing
  spaces or apostrophes and rejected `MAKEFILE_LIST` injection.
- Expanded the root-policy regressions across all six Make aliases to cover
  brackets plus command-line and environment overrides, and resolved portable
  shell helpers from `PATH`.

## 2026-06-18

- Replaced the broad overall-address expression with linear email shape validation
  for one separator and a dotted domain.
- Removed vendored Tornado stack traces and exception objects from HTTP error
  renderers, added generic HTML/JSON responses with opaque request IDs, and
  redacted request and exception values from structured server logs.

## 2026-06-17

- Added a request-owned signup submit busy state so accepted requests disable
  the semantic control and retryable terminal paths restore it without allowing
  stale callbacks to affect newer submissions.

## 2026-06-16

- Added signup request ownership so duplicate or delayed terminal XHR events
  cannot release a newer submission's in-flight lock.
- Added signup network failure release so transport errors and browser aborts
  restore the shared generic retry path instead of leaving the form locked.

## 2026-06-15

- Added a semantic signup submit control so pointer and keyboard activation use
  native email constraints before the shared dependency-free submit handler.
- Added a signup in-flight guard to prevent overlapping browser POSTs while
  preserving retry after completed failures.
- Added signup setup failure release so synchronous XHR setup or dispatch
  errors restore retry with generic text-only feedback.
- Added signup request timeout release so a stalled browser POST restores retry
  after a finite 10-second bound.
- Added retryable signup feedback that keeps the form available after completed,
  timeout, and synchronous setup failures.

## 2026-06-13

- Made every dependency-free Make alias resolve the static checker from the
  checkout when the Makefile is invoked by absolute path.
- Documented the `SignUp` datastore entity, plaintext email storage,
  deterministic idempotent key, and automatic creation timestamp.
- Recorded the retired Python 2 App Engine SDK boundary, historical local and
  deployment commands, and local datastore/export exclusions.

## 2026-06-12

- Disabled checkout credential persistence in the pinned, read-only hosted
  validation job and added structural checks for that boundary.

## 2026-06-10

- Added a signup body limit that rejects more than 4 KiB with a generic `413`
  before email argument access.
- Added GitHub Actions CI that runs the SDK-free `make check` baseline.
- Added idempotent signup keys using a prefixed SHA-256 digest of normalized
  email addresses to avoid duplicate retry entities and plaintext datastore keys.
- Added pinned, read-only Python 3.12 hosted validation for the dependency-free
  signup and App Engine configuration baseline.
- Added a signup form submit guard so Enter-key submissions use the same
  dependency-free XSRF-aware invite request handler as button clicks.

## 2026-06-08

- Added email normalization and validation before storing invite signups.
- Switched external template and stylesheet asset URLs to HTTPS.
- Removed template autoescape disabling and required secure App Engine handlers.
- Updated the signup form to use required email input semantics.
- Rendered the XSRF hidden field as explicit raw framework markup and switched
  signup status messages to text-only updates.
- Capped signup email input at the 254-character address boundary in both the
  template and server validator.
- Added email dot validation for leading, trailing, and consecutive dot cases.
- Added domain label validation for leading/trailing hyphens and labels over 63
  characters.
- Added domain label character validation for underscores, non-ASCII labels, and
  characters outside ASCII letters, digits, and interior hyphens.
- Added local-part validation for bounded unquoted ASCII signup addresses.
- Added top-level domain validation for one-character and all-numeric final
  labels.
- Added dependency-free signup JavaScript so invite requests no longer depend
  on remote jQuery.
- Added `make lint`, `make test`, and `make build` aliases so the standard
  gate commands run the same SDK-free static baseline as `make check`.
- Added local App Engine datastore artifact ignore rules.
- Added `make check` and an SDK-free baseline contract checker.
