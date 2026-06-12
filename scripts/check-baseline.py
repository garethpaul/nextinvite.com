#!/usr/bin/env python3
"""Static and dependency-free checks for the NextInvite App Engine sample."""

from pathlib import Path
import ast
import importlib.util
import re
import sys
import types


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = "docs/plans/2026-06-08-nextinvite-baseline.md"
LENGTH_PLAN_PATH = "docs/plans/2026-06-09-signup-email-length.md"
DOT_PLAN_PATH = "docs/plans/2026-06-09-signup-email-dot-validation.md"
DOMAIN_LABEL_PLAN_PATH = "docs/plans/2026-06-09-signup-domain-label-validation.md"
DOMAIN_LABEL_CHARACTER_PLAN_PATH = "docs/plans/2026-06-09-signup-domain-label-characters.md"
LOCAL_PART_PLAN_PATH = "docs/plans/2026-06-09-signup-email-local-part-validation.md"
TOP_LEVEL_DOMAIN_PLAN_PATH = "docs/plans/2026-06-09-signup-top-level-domain-validation.md"
MAKE_GATE_PLAN_PATH = "docs/plans/2026-06-09-make-gate-aliases.md"
SIGNUP_JS_PLAN_PATH = "docs/plans/2026-06-09-dependency-free-signup-javascript.md"
SIGNUP_FORM_SUBMIT_PLAN_PATH = "docs/plans/2026-06-10-signup-form-submit-guard.md"
IDEMPOTENT_SIGNUP_PLAN_PATH = "docs/plans/2026-06-10-idempotent-signup-key.md"
HOSTED_VALIDATION_PLAN_PATH = "docs/plans/2026-06-10-hosted-static-validation.md"
SIGNUP_BODY_LIMIT_PLAN_PATH = "docs/plans/2026-06-12-signup-body-limit.md"


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


def markdown_section(text, heading):
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def install_server_stubs():
    tornado = types.ModuleType("tornado")
    tornado_web = types.ModuleType("tornado.web")
    tornado_wsgi = types.ModuleType("tornado.wsgi")

    class RequestHandler:
        pass

    class WSGIApplication:
        def __init__(self, routes, **settings):
            self.routes = routes
            self.settings = settings

    tornado_web.RequestHandler = RequestHandler
    tornado_wsgi.WSGIApplication = WSGIApplication
    tornado.web = tornado_web
    tornado.wsgi = tornado_wsgi

    google = types.ModuleType("google")
    appengine = types.ModuleType("google.appengine")
    api = types.ModuleType("google.appengine.api")
    users = types.ModuleType("google.appengine.api.users")
    ext = types.ModuleType("google.appengine.ext")
    db = types.ModuleType("google.appengine.ext.db")

    users.get_current_user = lambda: None
    users.is_current_user_admin = lambda: False
    users.create_login_url = lambda uri: "/login?next=" + uri

    class Model:
        pass

    db.Model = Model
    db.TextProperty = lambda *args, **kwargs: None
    db.DateTimeProperty = lambda *args, **kwargs: None

    base = types.ModuleType("base")
    base.BaseHandler = RequestHandler

    sys.modules.update({
        "markdown": types.ModuleType("markdown"),
        "tornado": tornado,
        "tornado.web": tornado_web,
        "tornado.wsgi": tornado_wsgi,
        "google": google,
        "google.appengine": appengine,
        "google.appengine.api": api,
        "google.appengine.api.users": users,
        "google.appengine.ext": ext,
        "google.appengine.ext.db": db,
        "base": base,
    })


def load_server_module():
    install_server_stubs()
    spec = importlib.util.spec_from_file_location("nextinvite_server", str(ROOT / "next" / "server.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    failures = []
    required = [
        ".gitignore",
        ".github/workflows/check.yml",
        "CHANGES.md",
        "Makefile",
        "README.md",
        "SECURITY.md",
        "VISION.md",
        "next/app.yaml",
        "next/server.py",
        "next/templates/home.html",
        "next/static/style.css",
        PLAN_PATH,
        LENGTH_PLAN_PATH,
        DOT_PLAN_PATH,
        DOMAIN_LABEL_PLAN_PATH,
        DOMAIN_LABEL_CHARACTER_PLAN_PATH,
        LOCAL_PART_PLAN_PATH,
        TOP_LEVEL_DOMAIN_PLAN_PATH,
        MAKE_GATE_PLAN_PATH,
        SIGNUP_JS_PLAN_PATH,
        SIGNUP_FORM_SUBMIT_PLAN_PATH,
        IDEMPOTENT_SIGNUP_PLAN_PATH,
        HOSTED_VALIDATION_PLAN_PATH,
        SIGNUP_BODY_LIMIT_PLAN_PATH,
        "scripts/check-baseline.py",
    ]
    for path in required:
        require((ROOT / path).is_file(), f"required file missing: {path}", failures)

    for path in ["next/server.py", "next/base.py", "scripts/check-baseline.py"]:
        try:
            ast.parse(read(path), filename=path)
        except SyntaxError as error:
            failures.append(f"{path} must parse as Python: {error}")

    server = read("next/server.py")
    require("EMAIL_RE" in server and "normalize_email" in server and "is_valid_email" in server,
            "signup route must validate and normalize email addresses", failures)
    require("def signup_key_name(email)" in server and
            'hashlib.sha256(normalized_email.encode("utf-8")).hexdigest()' in server and
            "SignUp(key_name=signup_key_name(email))" in server,
            "signup persistence must use a deterministic hashed normalized-email key", failures)
    signup_post = server.split("class SignUpHandler", 1)[1].split("settings =", 1)[0]
    body_guard_index = signup_post.find("if len(request_body) > MAX_SIGNUP_BODY_BYTES")
    argument_index = signup_post.find("self.get_argument('email', '')")
    require("\nMAX_SIGNUP_BODY_BYTES = 4096\n" in server and
            "request_body = self.request.body or \"\"" in signup_post and
            0 <= body_guard_index < argument_index and
            "self.set_status(413)" in signup_post and
            'self.write("request too large")' in signup_post,
            "signup body must be bounded with a generic 413 before argument access", failures)
    require("has_valid_email_dots" in server,
            "signup route must reject unsafe email dot placement", failures)
    require("has_valid_domain_labels" in server and "len(label) <= 63" in server and
            'not label.startswith("-")' in server and 'not label.endswith("-")' in server,
            "signup route must validate domain label length and hyphen boundaries", failures)
    require("DOMAIN_LABEL_RE" in server and "[a-z0-9-]" in server,
            "signup route must validate domain label characters", failures)
    require("LOCAL_PART_RE" in server and "MAX_LOCAL_PART_LENGTH = 64" in server and
            "has_valid_local_part" in server,
            "signup route must validate local part length and characters", failures)
    require("has_valid_top_level_domain" in server and "top_level_label" in server and
            "character.isalpha()" in server,
            "signup route must validate top-level domain length and alphabetic content", failures)
    require("MAX_EMAIL_LENGTH = 254" in server and "len(email) <= MAX_EMAIL_LENGTH" in server,
            "signup route must enforce the 254-character email length limit", failures)
    require("self.set_status(400)" in server and 'self.write("invalid email")' in server,
            "invalid signup emails must return a deterministic 400", failures)
    require('"xsrf_cookies": True' in server, "XSRF protection must remain enabled", failures)

    template = read("next/templates/home.html")
    require("{% autoescape None %}" not in template,
            "home template must not disable autoescaping", failures)
    require("{% raw xsrf_form_html() %}" in template,
            "XSRF field must be rendered as explicit raw framework markup", failures)
    require("http://fonts.googleapis.com" not in template, "template font URL must use HTTPS", failures)
    require("ajax.googleapis.com" not in template and "jquery" not in template.lower(),
            "signup template must not depend on remote jQuery", failures)
    require("type='email'" in template and "required" in template,
            "signup form must use required email input", failures)
    require("maxlength='254'" in template,
            "signup form must expose the server email length limit", failures)
    require("request_invite(event)" in template and "if (event)" in template,
            "signup click handler must receive and guard the click event explicitly", failures)
    require('onsubmit="request_invite(event); return false;"' in template,
            "signup form submit event must use the dependency-free request handler", failures)
    require("new XMLHttpRequest()" in template and "request.open('POST', '/signup', true)" in template,
            "signup JavaScript must post to the absolute signup route without jQuery", failures)
    require("serialize_form" in template and "encodeURIComponent(field.name)" in template and "encodeURIComponent(field.value)" in template,
            "signup JavaScript must serialize form fields safely", failures)
    require("request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')" in template,
            "signup JavaScript must submit form-encoded data", failures)
    require("textContent" in template and ".html(" not in template,
            "signup JavaScript must handle responses without HTML injection", failures)

    style = read("next/static/style.css")
    require("http://s3.amazonaws.com" not in style, "background asset URL must use HTTPS", failures)

    app_yaml = read("next/app.yaml")
    require("runtime: python" in app_yaml and "script: server.py" in app_yaml,
            "App Engine runtime and script mapping must stay documented", failures)
    require(app_yaml.count("secure: always") >= 4,
            "all App Engine handlers must require secure transport", failures)

    makefile = read("Makefile")
    for expected in [
        ".PHONY: build check lint static-check test verify",
        "check: verify",
        "verify: static-check",
        "lint test build: static-check",
    ]:
        require(expected in makefile, f"Makefile must expose standard gate alias: {expected}", failures)

    gitignore = read(".gitignore")
    for expected in ["__pycache__/", "*.pyc", ".env", "appengine-generated/", "local_db.bin", "bulkloader-*"]:
        require(expected in gitignore, f".gitignore must include {expected}", failures)

    try:
        module = load_server_module()
        signup_key = module.signup_key_name(" User@Example.COM ")
        require(signup_key == module.signup_key_name("user@example.com"),
                "signup keys must be stable across email normalization variants", failures)
        require(signup_key.startswith("signup-") and len(signup_key) == 71 and "user@example.com" not in signup_key,
                "signup keys must use a prefixed SHA-256 digest without plaintext email", failures)
        require(module.normalize_email(" USER@Example.COM ") == "user@example.com",
                "normalize_email must trim and lowercase", failures)
        require(module.is_valid_email("user@example.com"), "valid email must be accepted", failures)
        require(module.is_valid_email("user+tag@example.com"),
                "plus-tagged local part must be accepted", failures)
        valid_254_email = ("a" * 64) + "@" + ("b" * 63) + "." + ("c" * 63) + "." + ("d" * 61)
        require(module.is_valid_email(valid_254_email),
                "254-character email must be accepted", failures)
        require(not module.is_valid_email(("a" * 65) + "@example.com"),
                "65-character local part must be rejected", failures)
        require(not module.is_valid_email("a@" + ("b" * 251) + ".c"),
                "255-character email must be rejected", failures)
        require(not module.is_valid_email(".user@example.com"),
                "leading-dot email local part must be rejected", failures)
        require(not module.is_valid_email("user.@example.com"),
                "trailing-dot email local part must be rejected", failures)
        require(not module.is_valid_email("user..name@example.com"),
                "consecutive-dot email local part must be rejected", failures)
        require(not module.is_valid_email("user@example..com"),
                "consecutive-dot email domain must be rejected", failures)
        require(not module.is_valid_email("user<>@example.com"),
                "angle-bracket local part must be rejected", failures)
        require(not module.is_valid_email("jos\u00e9@example.com"),
                "non-ASCII local part must be rejected", failures)
        require(not module.is_valid_email("user@-example.com"),
                "leading-hyphen domain label must be rejected", failures)
        require(not module.is_valid_email("user@example-.com"),
                "trailing-hyphen domain label must be rejected", failures)
        require(not module.is_valid_email("user@" + ("a" * 64) + ".com"),
                "64-character domain label must be rejected", failures)
        require(module.is_valid_email("user@sub-domain.example.com"),
                "interior-hyphen domain label must be accepted", failures)
        require(not module.is_valid_email("user@exa_mple.com"),
                "underscore domain label must be rejected", failures)
        require(not module.is_valid_email("user@\u00e9xample.com"),
                "non-ASCII domain label must be rejected", failures)
        require(module.is_valid_email("user@example.xn--p1ai"),
                "punycode-style top-level domain must be accepted", failures)
        require(not module.is_valid_email("user@example.c"),
                "single-character top-level domain must be rejected", failures)
        require(not module.is_valid_email("user@example.123"),
                "all-numeric top-level domain must be rejected", failures)
        require(not module.is_valid_email("not-an-email"), "invalid email must be rejected", failures)
    except Exception as error:
        failures.append(f"server helper contracts failed: {error}")

    docs = read("README.md") + "\n" + read("VISION.md") + "\n" + read("SECURITY.md")
    for phrase in ["make lint", "make test", "make build", "make check", "datastore", "private user data"]:
        require(phrase in docs.lower(), f"docs must mention {phrase}", failures)
    require("email dot validation" in docs.lower(),
            "docs must mention email dot validation", failures)
    require("domain label validation" in docs.lower(),
            "docs must mention domain label validation", failures)
    require("domain label character validation" in docs.lower(),
            "docs must mention domain label character validation", failures)
    require("local-part validation" in docs.lower(),
            "docs must mention local-part validation", failures)
    require("top-level domain validation" in docs.lower(),
            "docs must mention top-level domain validation", failures)
    require("dependency-free signup javascript" in docs.lower(),
            "docs must mention dependency-free signup JavaScript", failures)
    require("signup form submit guard" in docs.lower(),
            "docs must mention the signup form submit guard", failures)
    require("signup body limit" in docs.lower(),
            "docs must mention the signup body limit", failures)
    changes = read("CHANGES.md")
    require("email dot validation" in changes.lower(),
            "CHANGES must mention email dot validation", failures)
    require("domain label validation" in changes.lower(),
            "CHANGES must mention domain label validation", failures)
    require("domain label character validation" in changes.lower(),
            "CHANGES must mention domain label character validation", failures)
    require("local-part validation" in changes.lower(),
            "CHANGES must mention local-part validation", failures)
    require("top-level domain validation" in changes.lower(),
            "CHANGES must mention top-level domain validation", failures)
    require("dependency-free signup javascript" in changes.lower(),
            "CHANGES must mention dependency-free signup JavaScript", failures)
    require("signup form submit guard" in changes.lower(),
            "CHANGES must mention the signup form submit guard", failures)
    require("signup body limit" in changes.lower(),
            "CHANGES must mention the signup body limit", failures)
    for phrase in ["make lint", "make test", "make build", "make check"]:
        require(phrase in changes, f"CHANGES must mention {phrase}", failures)

    plan = read(PLAN_PATH)
    require("status: completed" in plan and "Verification" in plan,
            "plan must be completed and include verification", failures)
    length_plan = read(LENGTH_PLAN_PATH)
    require("status: completed" in length_plan and "254-character" in length_plan,
            "email length plan must record status and boundary", failures)
    dot_plan = read(DOT_PLAN_PATH) if (ROOT / DOT_PLAN_PATH).is_file() else ""
    require("status: completed" in dot_plan and "dot" in dot_plan,
            "email dot validation plan must record status and boundary", failures)
    domain_label_plan = read(DOMAIN_LABEL_PLAN_PATH) if (ROOT / DOMAIN_LABEL_PLAN_PATH).is_file() else ""
    require("status: completed" in domain_label_plan and "domain label" in domain_label_plan.lower(),
            "domain label validation plan must record status and boundary", failures)
    domain_label_character_plan = read(DOMAIN_LABEL_CHARACTER_PLAN_PATH) if (ROOT / DOMAIN_LABEL_CHARACTER_PLAN_PATH).is_file() else ""
    require("status: completed" in domain_label_character_plan and "make check" in domain_label_character_plan,
            "domain label character validation plan must record status and verification", failures)
    local_part_plan = read(LOCAL_PART_PLAN_PATH) if (ROOT / LOCAL_PART_PLAN_PATH).is_file() else ""
    require("status: completed" in local_part_plan and "make check" in local_part_plan,
            "local-part validation plan must record status and verification", failures)
    top_level_domain_plan = read(TOP_LEVEL_DOMAIN_PLAN_PATH) if (ROOT / TOP_LEVEL_DOMAIN_PLAN_PATH).is_file() else ""
    require("status: completed" in top_level_domain_plan and "make check" in top_level_domain_plan,
            "top-level domain validation plan must record status and verification", failures)
    make_gate_plan = read(MAKE_GATE_PLAN_PATH) if (ROOT / MAKE_GATE_PLAN_PATH).is_file() else ""
    require("status: completed" in make_gate_plan and "make lint" in make_gate_plan and "make build" in make_gate_plan,
            "make gate alias plan must record status and verification", failures)
    signup_js_plan = read(SIGNUP_JS_PLAN_PATH) if (ROOT / SIGNUP_JS_PLAN_PATH).is_file() else ""
    require("status: completed" in signup_js_plan and "make check" in signup_js_plan,
            "dependency-free signup JavaScript plan must record status and verification", failures)
    signup_submit_plan = read(SIGNUP_FORM_SUBMIT_PLAN_PATH) if (ROOT / SIGNUP_FORM_SUBMIT_PLAN_PATH).is_file() else ""
    require("status: completed" in signup_submit_plan and "make check" in signup_submit_plan,
            "signup form submit guard plan must record status and verification", failures)
    idempotent_signup_plan = read(IDEMPOTENT_SIGNUP_PLAN_PATH) if (ROOT / IDEMPOTENT_SIGNUP_PLAN_PATH).is_file() else ""
    require("status: completed" in idempotent_signup_plan and "make check" in idempotent_signup_plan,
            "idempotent signup key plan must record status and verification", failures)
    signup_body_limit_plan = read(SIGNUP_BODY_LIMIT_PLAN_PATH) if (ROOT / SIGNUP_BODY_LIMIT_PLAN_PATH).is_file() else ""
    signup_body_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", signup_body_limit_plan)
    signup_body_work = markdown_section(signup_body_limit_plan, "Work Completed")
    signup_body_verification = markdown_section(signup_body_limit_plan, "Verification Completed")
    require(signup_body_status == ["completed"] and bool(signup_body_work),
            "signup body limit plan must record one completed status and completed work", failures)
    require(bool(signup_body_verification) and not re.search(
                r"(?i)\b(?:pending|todo|tbd|not run)\b", signup_body_verification),
            "signup body limit plan must record completed verification", failures)
    for evidence in [
        "python3 -m py_compile scripts/check-baseline.py",
        "make lint",
        "make test",
        "make build",
        "make check",
        "git diff --check",
        "27397766640",
        "27397768643",
        "38ec086796059511cc29df438e6c23e010a456cd",
        "MAX_SIGNUP_BODY_BYTES = 4096",
        'request_body = self.request.body or ""',
        "if len(request_body) > MAX_SIGNUP_BODY_BYTES",
        "self.set_status(413)",
        'self.write("request too large")',
        "self.get_argument('email', '')",
    ]:
        require(evidence in signup_body_verification,
                f"signup body verification must record {evidence}", failures)
    hosted_plan = read(HOSTED_VALIDATION_PLAN_PATH) if (ROOT / HOSTED_VALIDATION_PLAN_PATH).is_file() else ""
    workflow = read(".github/workflows/check.yml")
    require("status: completed" in hosted_plan and "make check" in hosted_plan,
            "hosted static validation plan must record status and verification", failures)
    for expected in [
        "permissions:\n  contents: read",
        "cancel-in-progress: true",
        "runs-on: ubuntu-24.04",
        "timeout-minutes: 10",
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
        "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
        'python-version: "3.12"',
        "run: make check",
    ]:
        require(expected in workflow, f"Check workflow must keep {expected}", failures)

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("nextinvite baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
