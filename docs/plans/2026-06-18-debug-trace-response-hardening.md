# Debug Trace Response Hardening

Status: accepted for implementation

## Problem

The vendored Tornado `RequestHandler.write_error` writes uncaught exception
tracebacks into HTTP responses whenever the application `debug` setting is
true. `next/server.py` derives that setting from the legacy
`SERVER_SOFTWARE` environment variable, so a misclassified or reachable local
deployment can disclose source paths, exception messages, and stack frames.

## Decision

The default vendored error renderer will always return the existing generic
status response, regardless of the `debug` setting or the presence of
`exc_info`. The framework's existing `_handle_request_exception` path will
continue to log uncaught exceptions with `exc_info=True` before rendering the
generic response. Custom `write_error` and legacy `get_error_html` overrides
will keep receiving exception context for compatibility.

The application will set `debug` to `False` explicitly instead of inferring it
from `SERVER_SOFTWARE`. Local debugging remains available through server-side
logs; HTTP responses are not a debugging channel.

## Alternatives

1. Override only the application's handler. Rejected because the active
   vendored framework sink would remain and future handlers could bypass the
   override.
2. Remove `exc_info` before error rendering. Rejected because it would break
   compatible custom error handlers and is unnecessary to prevent the default
   response disclosure.
3. Exclude the vendored source from CodeQL. Rejected because it hides the
   alert without changing runtime behavior.

## Verification

Tests will execute the real vendored error methods through a Python 2-to-3
compatibility harness and prove that both `debug=False` and `debug=True`
produce the same generic response for a sentinel exception. The same exercise
will prove that the sentinel exception remains in server-side logging. A
separate application contract will prove that a legacy development-shaped
`SERVER_SOFTWARE` value cannot enable debug mode.

The repository baseline, Python 2 grammar conversion, workflow validation,
and hosted CodeQL analysis must pass before publication.

## Deployment Boundary

This change reduces one active-code disclosure path; it does not make the
retired Python 2 App Engine application safe to redeploy. Runtime migration
remains P0 before any redeployment.
