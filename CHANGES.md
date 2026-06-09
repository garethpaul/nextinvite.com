# Changes

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
- Added local App Engine datastore artifact ignore rules.
- Added `make check` and an SDK-free baseline contract checker.
