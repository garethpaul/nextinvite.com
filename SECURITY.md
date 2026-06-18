# Security Policy

## Supported Versions

The supported security scope for `nextinvite.com` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: NextInvite repo

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/nextinvite.com` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be a public sample, documentation, or utility project. The active security scope is the code and documentation on the default branch.
- Review found authentication, token, or session-related code paths; changes in those areas should receive security-focused review before merge.
- Review found external API integrations or credential-adjacent configuration; changes in those areas should receive security-focused review before merge.
- Review found network clients, sockets, web APIs, or service endpoints; changes in those areas should receive security-focused review before merge.
- Review found mobile permission or privacy-sensitive data handling; changes in those areas should receive security-focused review before merge.
- Review found file, document, data, or media parsing flows; changes in those areas should receive security-focused review before merge.
- Review found shell execution, subprocess, or dynamic evaluation surfaces; changes in those areas should receive security-focused review before merge.
- Review found database, model, query, or persistence-related code; changes in those areas should receive security-focused review before merge.
- Review found infrastructure, deployment, proxy, or cloud configuration; changes in those areas should receive security-focused review before merge.
- Review found secret-like configuration names that require careful review before use; changes in those areas should receive security-focused review before merge.
- No primary dependency manifest was detected in the repository root. If dependencies are added later, include a manifest and prefer reproducible installation instructions.
- Run `make lint`, `make test`, `make build`, and `make check` after changing
  signup routes, templates, App Engine config, vendored dependency boundaries,
  or security docs.
- The pinned Linux workflow uses a read-only, credential-free checkout and runs
  only dependency-free local checks without App Engine deployment, datastore
  access, external service calls, or persisted repository credentials.
- Signup emails are private user data. Do not commit datastore exports, request logs, local App Engine data, `.env` files, or production configuration.
- The `SignUp` entity stores normalized email as plaintext private data. Its
  deterministic SHA-256 key name provides retry idempotency, not encryption or
  protection from guessing known addresses.
- Signup email inputs should stay normalized, format-checked, and capped at the 254-character address boundary before datastore persistence.
- The signup body limit should reject more than 4 KiB before handler argument
  access and return a generic `413` without echoing private form content.
- Idempotent signup keys should hash normalized addresses with SHA-256 so retry
  deduplication does not expose plaintext email in datastore identifiers; this
  is deterministic hashing, not encryption.
- Email dot validation should reject leading, trailing, and consecutive dot cases before datastore persistence.
- Domain label validation should reject leading/trailing hyphen labels and
  labels over 63 characters before datastore persistence.
- Domain label character validation should reject underscores, non-ASCII labels,
  and other characters outside ASCII letters, digits, and interior hyphens.
- Local-part validation should accept bounded unquoted ASCII local parts and
  reject unsafe or non-ASCII characters before datastore persistence.
- Top-level domain validation should reject one-character or all-numeric final
  labels before datastore persistence.
- Linear email shape validation should require exactly one separator and a
  dotted domain without evaluating a broad overall-address regular expression.
- Dependency-free signup JavaScript should keep the invite form independent of
  remote jQuery while preserving XSRF form serialization.
- The signup form submit guard should keep keyboard form submissions on the
  same dependency-free, XSRF-aware request path as click submissions.
- The semantic signup submit control should keep pointer activation behind
  native form constraints and the XSRF-aware submit event.
- The signup in-flight guard should prevent overlapping browser POSTs while
  preserving retry after a completed failure.
- The signup setup failure release should restore retry without exposing
  exception details when XHR setup or synchronous dispatch fails.
- The signup request timeout release should bound a stalled browser request to
  10 seconds and restore retry with generic text-only failure feedback.
- Retryable signup feedback should remain text-only, preserve the form, and
  avoid exposing response bodies, exception details, or submitted addresses.
- The signup network failure release should handle transport errors and browser
  aborts through the same generic text-only retry path.
- Signup request ownership should make duplicate or delayed terminal XHR events
  inert after a newer submission owns the global signup state.
- The signup submit busy state should disable the semantic control only for the
  active XHR and restore it only through that request's retryable release path.
- App Engine handlers should keep `secure: always`, and templates should not disable Tornado autoescaping.
- Classic `dev_appserver.py` and `appcfg.py` workflows require an
  era-compatible SDK. Keep local datastore files and exports out of git, and do
  not deploy without an owned App Engine project, reviewed settings, explicit
  credentials, and a separate deployment plan.

## Service and API Notes

For web services, APIs, sockets, or scraping workflows, prioritize reports involving authentication bypass, authorization errors, injection, server-side request forgery, unsafe deserialization, credential leakage, data exposure, or denial-of-service conditions. Use test accounts and minimal proof-of-concept traffic only.

For this app, reports involving dependency-free signup JavaScript should state
whether the invite form can be made to depend on remote scripts or inject HTML
through status messages.
Reports involving the signup form submit guard should state whether keyboard
submission bypasses the dependency-free XSRF-aware request handler.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, datastore exports, private signup data, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
