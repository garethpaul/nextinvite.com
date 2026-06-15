# Signup In-Flight Guard

status: in progress

## Context

The form submit handler and styled link both call `request_invite`. Until the
first asynchronous response completes, repeated clicks or submissions create
overlapping POST requests. The datastore key prevents duplicate entities, but
the browser still performs redundant requests and response races.

## Requirements

- Allow only one signup XHR to be in flight at a time.
- Set the guard before opening or sending the request.
- Keep successful completion terminal because the form is replaced.
- Release the guard after a completed non-success response so the user can retry.
- Preserve event cancellation, form serialization, XSRF submission, response
  messaging, backend validation, and idempotent datastore keys.

## Implementation

1. Add one script-level boolean for signup request ownership.
2. Return early when a request is already pending and set ownership before XHR
   setup.
3. Release ownership only on the completed failure path.
4. Add ordering-sensitive static checks and project guidance.

## Verification

- Run checker compilation and all four Make gates from the checkout plus the
  rooted canonical gate from an external directory.
- Verify isolated mutations that remove the early guard, move ownership after
  request setup, release before completion, keep failures locked, remove
  guidance, or leave this plan incomplete are rejected.
- Run `git diff --check` and exact intended-path, generated-artifact,
  secret-pattern, conflict-marker, binary, and large-file audits.

## Risks

- This guard is page-local and does not replace server-side idempotency.
- The stacked base pull request must remain available and merge first.

## Work Completed

- Pending implementation.

## Verification Completed

- Pending validation.
