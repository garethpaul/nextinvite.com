# Signup POST-Body Ownership

Status: Completed

## Goal

Prevent private signup email values from being accepted through URL query
parameters while preserving the existing native and asynchronous form paths.

## Scope

- Read the email only from the bounded raw POST body.
- Accept only `application/x-www-form-urlencoded`, including charset options.
- Keep normalized validation, XSRF enforcement, persistence, and responses.
- Reject query-only and unsupported-content requests with generic HTTP 400.

## Verification

- Prove the query-only persistence defect before implementation.
- Prove unsupported raw text bodies fail closed.
- Run focused signup persistence coverage and `make check`.
- Run hostile mutations and `git diff --check` before review.

## Outcome

Query-only signup emails no longer reach persistence. Valid URL-encoded body
emails retain normalization and the existing successful response.
