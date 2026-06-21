# Spaced Absolute Makefile Path Verification

status: completed

## Context

GNU Make list functions split a loaded absolute Makefile path at spaces. A
checkout path containing spaces, brackets, and an apostrophe therefore sent
all dependency-free verification scripts to a fabricated caller path.

## Scope

1. Derive the checkout root from the complete `MAKEFILE_LIST` value.
2. Preserve the authoritative root against command-line and environment input.
3. Reject command-line or environment-preferred `MAKEFILE_LIST` overrides.
4. Exercise all six Make aliases from an external working directory.

## Verification

- Root and external hostile-path gates passed on supported Python 3.12.
- All six Make aliases retained the checkout with no override and with
  command-line or environment `ROOT` input.
- Both tested `MAKEFILE_LIST` override paths failed closed.
- Vendored Tornado containment and finish compatibility tests remained green;
  no fixture or vendored runtime bytes changed.

## Risk And Rollback

This changes dependency-free verification root discovery only. It does not
alter App Engine behavior, datastore access, signup delivery, or Tornado code.
