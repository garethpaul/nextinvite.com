## NextInvite.com Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

NextInvite.com is a Google App Engine-era Python app that stores data in the
App Engine datastore.

The repository is useful as a preserved App Engine/Tornado-style web app sample
with templates, static assets, datastore code, and vendored Tornado modules.
Project context lives in [`next/README`](next/README).

The goal is to keep the app recoverable while making datastore, hosting, and
legacy dependency assumptions explicit.

The current focus is:

Priority:

- Preserve the App Engine app structure under `next/`
- Keep datastore behavior and templates easy to inspect
- Avoid committing production secrets or private user data
- Keep signup templates autoescaped and App Engine handlers on secure transport
- Maintain security policy for the app
- Keep signup email handling validated and covered by static contracts
- Keep idempotent signup keys derived from normalized email hashes
- Keep signup email length limits aligned between the template and route handler
- Keep email dot validation in place before datastore persistence
- Keep domain label validation in place before datastore persistence
- Keep domain label character validation in place before datastore persistence
- Keep local-part validation in place before datastore persistence
- Keep top-level domain validation in place before datastore persistence
- Keep dependency-free signup JavaScript in place for the invite form
- Keep the signup form submit guard on the dependency-free invite request path
- Keep the semantic signup submit control behind native form validation
- Keep the signup in-flight guard around asynchronous form submissions
- Keep the signup setup failure release around synchronous XHR construction and send
- Keep retryable signup feedback separate from terminal success replacement
- Keep the signup network failure release on every terminal XHR failure path
- Keep the signup body limit before signup argument access
- Keep `make lint`, `make test`, `make build`, and `make check` on the
  SDK-free static baseline
- Keep that dependency-free baseline pinned, read-only, and credential-free in
  hosted Linux CI
- Keep the `SignUp` entity contract explicit: normalized plaintext email,
  automatic creation timestamp, and deterministic idempotent key name
- Keep hash-derived datastore keys documented as idempotency, not encryption
- Keep classic App Engine local development and deployment commands labeled
  historical and unverified without an era-compatible SDK
- Keep local datastore files, exports, credentials, and production user data
  outside version control

Next priorities:

- Add root-level setup and deployment notes
- Modernize App Engine/Tornado dependencies in a dedicated pass
- Expand route/template verification with fixture data

Contribution rules:

- One PR = one focused route, datastore, dependency, or documentation change.
- Keep private data and credentials out of git.
- Verify affected routes locally before pushing.
- Preserve signup input validation boundaries before datastore writes.
- Preserve email dot validation when changing signup handling.
- Preserve domain label validation when changing signup handling.
- Preserve domain label character validation when changing signup handling.
- Preserve local-part validation when changing signup handling.
- Preserve top-level domain validation when changing signup handling.
- Preserve dependency-free signup JavaScript when changing the invite form.
- Preserve the signup form submit guard when changing invite form behavior.
- Preserve the semantic signup submit control when changing invite actions.
- Preserve the signup network failure release when changing XHR event handling.
- Preserve the signup body limit when changing signup request handling.
- Preserve idempotent signup key generation when changing datastore writes.
- Run `make lint`, `make test`, `make build`, and `make check` before pushing
  route, template, or validation changes.
- Preserve license and provenance for vendored dependencies.

## Security And Privacy

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Datastore-backed apps can hold user data. Do not commit datastore exports,
session secrets, or production configuration.
Dependency-free signup JavaScript should avoid remote script dependencies while
submitting only form-encoded invite requests.
The signup form submit guard should keep keyboard submissions on the same
form-encoded request path as click submissions.
Idempotent signup keys should keep retries on one datastore entity without
placing plaintext addresses in datastore identifiers.

## What We Will Not Merge (For Now)

- Private datastore exports
- Production credentials or secrets
- Broad hosting migration without a deployment plan
- Vendored dependency changes without provenance

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
