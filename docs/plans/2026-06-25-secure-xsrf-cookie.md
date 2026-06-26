# Secure XSRF Cookie

## Status: Completed

## Context

The preserved Tornado XSRF implementation creates a browser cookie when a
visitor first renders the signup form. All App Engine handlers already use
`secure: always`, but that fresh cookie did not carry `Secure` or `HttpOnly`.
The application JavaScript serializes the server-rendered hidden XSRF field and
does not read `document.cookie`, so script access is unnecessary.

## Design

Add an opt-in `xsrf_cookie_kwargs` application setting to the contained
vendored Tornado subset. Keep the framework default empty for compatibility.
Configure production cookies with `secure=True` and `httponly=True`; preserve
classic `dev_appserver.py` HTTP compatibility by omitting only `Secure` when
`SERVER_SOFTWARE` identifies the development server.

Extend the converted synthetic WSGI smoke to render a fresh session without an
existing cookie and assert the emitted `_xsrf` cookie has both attributes. Keep
the existing known-token form and duplicate-signup route smoke unchanged.

## Work Completed

- Added application-owned XSRF cookie keyword arguments to the WSGI subset.
- Opted production signup traffic into `Secure` and `HttpOnly` while keeping
  the historical HTTP development server usable with `HttpOnly` alone.
- Added fresh-cookie behavior and application-setting assertions to the
  converted route smoke.
- Added six hostile source mutations covering both flags, development
  detection, framework wiring, browser cookie access, and HTTPS ownership.
- Added portable source contracts and synchronized security documentation.

## Verification

- The converted WSGI smoke failed before implementation with a fresh cookie
  containing only `_xsrf=<token>; Path=/`.
- `PYTHONDONTWRITEBYTECODE=1 python3 tests/test_vendored_tornado_surface.py`.
- Six isolated hostile XSRF cookie mutations are rejected.
- `/usr/bin/make check`.
- `git diff --check`.

## Evidence

- Python 2.7 `Cookie.Morsel` documents `secure` and `httponly` as supported
  attributes: https://docs.python.org/2.7/library/cookie.html
- Legacy App Engine documents `secure: always` as redirecting matching HTTP
  requests to HTTPS: https://cloud.google.com/appengine/docs/legacy/standard/python/config/appref

## Scope Boundaries

- Token generation, equality checks, hidden form fields, request validation,
  signup persistence, public routes, and cookie defaults for any other vendored
  application remain unchanged.
- No classic App Engine SDK or live deployment was available.
