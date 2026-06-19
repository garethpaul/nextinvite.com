# Signup Body Limit

status: completed

## Context

`SignUpHandler.post()` reads the email argument without an application-level
request body ceiling. Email validation caps the normalized address at 254
characters, but an oversized form body can still reach handler parsing before
that field validation runs.

## Priorities

1. Reject signup request bodies larger than 4 KiB before argument access.
2. Return a generic `413` response without echoing submitted content.
3. Preserve XSRF handling, email validation, and idempotent persistence.
4. Protect guard ordering with the dependency-free static checker.

## Implementation Units

### Signup Handler

File: `next/server.py`

Define a 4 KiB body ceiling and check `self.request.body` before calling
`get_argument`. Treat a missing body as empty and return `request too large`
for overflow.

### Static Contract And Documentation

Files:

- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-12-signup-body-limit.md`

Require the size, status, generic error, and pre-argument ordering. Document
that the guard bounds application handling rather than upstream transport
buffering.

## Work Completed

- Added a 4 KiB application-level signup body limit.
- Checked the body size before reading the email argument.
- Returned a generic `413` response for oversized requests.
- Preserved the existing XSRF, email-validation, and idempotent persistence
  contracts.

## Verification Completed

Completed locally on 2026-06-12:

- `python3 -m py_compile scripts/check-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- hostile mutations changing the limit or 413 response, or moving argument
  access before the guard, were each rejected by the static contract
- `git diff --check`

Completed on GitHub Actions for final head
`38ec086796059511cc29df438e6c23e010a456cd`:

- push run `27397766640`: success
- pull-request run `27397768643`: success

The verified implementation preserves `MAX_SIGNUP_BODY_BYTES = 4096`,
`request_body = self.request.body or ""`,
`if len(request_body) > MAX_SIGNUP_BODY_BYTES`, `self.set_status(413)`, and
`self.write("request too large")` before `self.get_argument('email', '')`.

## Boundaries

- Do not include submitted email or body content in errors.
- Do not weaken XSRF, email, or persistence contracts.
- Do not claim to change App Engine or Tornado transport buffering.
