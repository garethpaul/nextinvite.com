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
- Keep signup email length limits aligned between the template and route handler
- Keep email dot validation in place before datastore persistence
- Keep domain label validation in place before datastore persistence

Next priorities:

- Add root-level setup and deployment notes
- Document datastore entities and local development requirements
- Modernize App Engine/Tornado dependencies in a dedicated pass
- Expand route/template verification with fixture data

Contribution rules:

- One PR = one focused route, datastore, dependency, or documentation change.
- Keep private data and credentials out of git.
- Verify affected routes locally before pushing.
- Preserve signup input validation boundaries before datastore writes.
- Preserve email dot validation when changing signup handling.
- Preserve domain label validation when changing signup handling.
- Preserve license and provenance for vendored dependencies.

## Security And Privacy

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Datastore-backed apps can hold user data. Do not commit datastore exports,
session secrets, or production configuration.

## What We Will Not Merge (For Now)

- Private datastore exports
- Production credentials or secrets
- Broad hosting migration without a deployment plan
- Vendored dependency changes without provenance

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
