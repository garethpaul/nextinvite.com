# Linear Email Shape Validation

Status: planned

## Problem

The signup validator begins with a broad regular expression that checks the
overall email shape before running the existing bounded local-part, domain
label, top-level-domain, dot, and length validators. CodeQL reports that shape
expression as polynomial regular-expression denial of service at
`next/server.py:20`. The input length cap limits runtime exposure, but keeping a
flagged and redundant expression leaves avoidable security debt in the request
path.

## Requirements

- Replace the broad overall-shape expression with explicit linear-time checks
  for exactly one `@` separator and a dotted domain.
- Preserve the 254-character address limit, 64-character local-part limit,
  local-part character and dot rules, domain-label character and length rules,
  and top-level-domain validation.
- Keep valid ASCII and punycode-style signup addresses accepted while rejecting
  missing separators, multiple separators, missing domain dots, blank parts,
  and the existing invalid-address cases.
- Add mutation-sensitive portable contracts that reject restoration of the
  flagged expression or removal of either structural boundary.
- Synchronize operator, security, product, change, and completion evidence.

## Implementation Units

### U1: Linear structural validation

Files:

- `next/server.py`

Remove the broad overall-shape regular expression and add a small helper that
splits the bounded address once, requires exactly two nonempty parts, and
requires a dot in the domain before the existing validators run.

Test scenarios:

- A conventional address and a punycode-style top-level domain remain valid.
- Addresses without `@`, with multiple `@` characters, with blank parts, or
  without a domain dot are rejected.
- Existing length, local-part, dot, domain-label, and top-level-domain cases
  retain their behavior.

### U2: Portable regression contracts

Files:

- `scripts/check-baseline.py`

Require the linear helper, its position in the validation chain, the absence of
the flagged broad expression, and runtime coverage of the structural boundary.

Test scenarios:

- All repository and external-directory Make gates accept the implementation.
- Isolated mutations restoring the broad expression or removing the
  single-separator, nonempty-part, dotted-domain, helper-call, guidance, or
  completed-plan contracts are rejected.

### U3: Guidance and evidence

Files:

- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-18-linear-email-shape-validation.md`

Document the linear structural boundary and record exact completed validation.

## Validation

- Run checker compilation and all Make aliases from the checkout, plus the
  absolute Makefile check from an external directory.
- Run isolated hostile mutations for implementation, ordering, documentation,
  and completed-plan requirements.
- Audit the exact diff, generated artifacts, secret signatures, conflict
  markers, binaries, large files, modes, and whitespace before committing.

## Risks

- Portable static validation cannot reproduce GitHub's CodeQL analysis or
  execute the retired App Engine production runtime.
- Structural checks intentionally remain narrower than full RFC mailbox syntax,
  matching the signup product's existing unquoted ASCII address policy.
- This change is stacked on PR #14, which must remain open and merge first.

## Work Completed

Pending implementation.

## Verification Completed

Pending implementation and validation.
