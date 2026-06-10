# Changes

## 2026-06-10

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
