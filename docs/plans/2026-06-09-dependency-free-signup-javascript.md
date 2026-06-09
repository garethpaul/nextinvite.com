# Dependency-Free Signup JavaScript

status: completed

## Context

The invite form used remote jQuery for a single signup POST and response
message update. That added a third-party script dependency to a simple flow that
already had a small, local template.

## Objectives

- Remove the remote jQuery script include.
- Submit `/signup` with dependency-free `XMLHttpRequest`.
- Preserve XSRF hidden-field serialization by encoding all named form fields.
- Preserve text-only success and validation-error messages.
- Extend the SDK-free static baseline and docs so the form stays independent of
  remote jQuery.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
