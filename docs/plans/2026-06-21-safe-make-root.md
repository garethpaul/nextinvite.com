# Safe Make Root

## Problem

The documented absolute `make -f` command derived its repository root with GNU
Make list functions, which split checkout paths on whitespace and accepted a
caller-controlled `MAKEFILE_LIST` value.

## Change

- Resolve the raw Makefile path with POSIX-compatible shell tooling.
- Reject non-file origins for GNU Make's automatic `MAKEFILE_LIST` value.
- Cover spaces, a literal apostrophe, and command-line injection without running
  application or datastore code.

## Validation

- Run every Make alias and all three policy test files.
- Run the static checker, git integrity checks, and a current-tree secret scan.
- Confirm the exact pull-request head passes pinned Ubuntu CI and CodeQL.
