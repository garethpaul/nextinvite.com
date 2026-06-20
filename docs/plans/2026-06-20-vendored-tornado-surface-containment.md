# Vendored Tornado Surface Containment Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Limit the preserved App Engine application to the vendored Tornado modules it actually imports and remove the response-body shortcut that CodeQL treats as a tainted HTTP sink.

**Architecture:** Keep the existing Python 2 App Engine and Tornado WSGI behavior, but reduce the vendored package to the static import closure rooted at `tornado.web` and `tornado.wsgi`. Enforce the boundary with a Python 3 structural regression test, and make every internal response body write explicit before calling a bodyless `finish()`.

**Tech Stack:** Python 2 source, Python 3 structural tests, GNU Make, GitHub Actions, CodeQL.

---

### Task 1: Add the failing containment contract

**Files:**
- Create: `tests/test_vendored_tornado_surface.py`

1. Assert that the vendored package contains only the nine modules in the WSGI import closure.
2. Assert that the non-executed upstream `next/tornado/test` suite is absent.
3. Assert that `RequestHandler.finish` accepts no response chunk and that no internal caller passes one.
4. Run `python3 tests/test_vendored_tornado_surface.py`; expect failure against the current oversized package and `finish(chunk)` API.

### Task 2: Prune unreachable framework code

**Files:**
- Delete: unused `next/tornado` modules and subdirectories outside the WSGI closure
- Modify: `next/tornado/web.py`

1. Delete modules not reachable from `next/server.py` or `next/base.py` through `tornado.web` and `tornado.wsgi`.
2. Replace internal `finish(body)` calls with explicit `write(body)` followed by `finish()`.
3. Remove the `chunk` parameter and implicit write from `RequestHandler.finish`.
4. Run the focused containment test; expect pass.

### Task 3: Integrate and document the boundary

**Files:**
- Modify: `Makefile`
- Modify: `README.md`
- Modify: `SECURITY.md`
- Modify: `VISION.md`
- Modify: `AGENTS.md`
- Modify: `docs/readme-overview.svg`

1. Run the containment test from every Make verification alias.
2. Document the preserved WSGI-only subset and distinguish it from a current supported Tornado release.
3. Remove stale references to the deleted upstream tests and unused auth/network modules.
4. Run focused tests, `make check`, Actionlint, diff checks, and a changed-tree secret scan.

### Task 4: Publish and verify

1. Push the branch and open a focused pull request with alert provenance and runtime reachability evidence.
2. Wait for exact-head hosted checks and CodeQL.
3. Merge normally only when required checks pass and the open-alert delta matches the intended containment.
4. Verify the default branch SHA and remaining alerts.
