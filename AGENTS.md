# AGENTS.md

## Repository purpose

`garethpaul/nextinvite.com` is a static web project. NextInvite repo

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `tests` - tests and fixtures
- `next` - repository source or sample assets

## Development commands

- Install dependencies: no repository-specific install command is documented.
- Full baseline: `make check`
- Combined verification: `make verify`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: Python (54), C (1).

## Testing guidance

- Test-related files detected: `next/tornado/test/`, `next/tornado/test/auth_test.py`, `next/tornado/test/curl_httpclient_test.py`, `next/tornado/test/escape_test.py`, `next/tornado/test/gen_test.py`, `next/tornado/test/httpclient_test.py`, `next/tornado/test/httpserver_test.py`, `next/tornado/test/httputil_test.py`, `next/tornado/test/import_test.py`, `next/tornado/test/ioloop_test.py`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- Detected references to Parse, Twitter. Keep API keys, OAuth credentials, tokens, and account-specific values in local configuration only.
- Keep App Engine generated files, datastore exports, logs, `.env` files, and private signup email data out of git.
- Signup emails are private user data. Do not commit datastore exports or logs containing submitted addresses.
- The signup form and server validator both enforce the 254-character email length boundary before persistence.
- Email dot validation rejects leading, trailing, and consecutive dot cases before persistence.
- Domain label validation rejects leading/trailing hyphen labels and labels over 63 characters before persistence.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
