# Changes

## 2026-06-08

- Added email normalization and validation before storing invite signups.
- Switched external template and stylesheet asset URLs to HTTPS.
- Removed template autoescape disabling and required secure App Engine handlers.
- Updated the signup form to use required email input semantics.
- Rendered the XSRF hidden field as explicit raw framework markup and switched
  signup status messages to text-only updates.
- Added local App Engine datastore artifact ignore rules.
- Added `make check` and an SDK-free baseline contract checker.
