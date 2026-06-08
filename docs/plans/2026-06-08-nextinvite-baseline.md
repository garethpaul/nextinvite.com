# NextInvite Baseline Plan

Date: 2026-06-08

status: completed

## Context

`nextinvite.com` is a preserved Google App Engine-era Python app that renders a
signup page and stores invite email addresses in the App Engine datastore. It
uses vendored Tornado modules and an old App Engine runtime, so verification
needs to avoid requiring a live SDK.

## Objectives

- Validate and normalize signup email addresses before storing them.
- Keep XSRF protection enabled on the Tornado WSGI application.
- Avoid insecure HTTP asset URLs in the template and stylesheet.
- Require secure App Engine handlers and keep template autoescaping enabled.
- Keep the signup form using browser-native email validation.
- Add an SDK-free `make check` gate for route, template, config, and docs
  contracts.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
