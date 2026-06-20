#!/usr/bin/env python3
"""Static and dependency-free checks for the NextInvite App Engine sample."""

from pathlib import Path
import ast
import importlib.util
import re
import sys
import types


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_MAKEFILE = """override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: build check lint static-check test verify

PYTHON ?= python3

check: verify

verify: static-check

lint test build: static-check

static-check:
\tPYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/check-baseline.py"
\tPYTHONDONTWRITEBYTECODE=1 $(PYTHON) -W ignore::DeprecationWarning "$(ROOT)/tests/test_debug_trace_policy.py"
\tPYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/tests/test_vendored_tornado_surface.py"
"""
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
CI_PLAN_PATH = "docs/plans/2026-06-10-ci-baseline.md"
IDEMPOTENT_SIGNUP_PLAN_PATH = "docs/plans/2026-06-10-idempotent-signup-key.md"
HOSTED_VALIDATION_PLAN_PATH = "docs/plans/2026-06-10-hosted-static-validation.md"
SIGNUP_BODY_LIMIT_PLAN_PATH = "docs/plans/2026-06-12-signup-body-limit.md"
CHECKOUT_CREDENTIAL_PLAN_PATH = "docs/plans/2026-06-12-checkout-credential-boundary.md"
DATASTORE_LOCAL_DEVELOPMENT_PLAN_PATH = "docs/plans/2026-06-13-datastore-local-development.md"
LOCATION_INDEPENDENT_MAKE_PLAN_PATH = "docs/plans/2026-06-13-location-independent-make.md"
SIGNUP_IN_FLIGHT_PLAN_PATH = "docs/plans/2026-06-15-signup-in-flight-guard.md"
SIGNUP_SETUP_FAILURE_PLAN_PATH = "docs/plans/2026-06-15-signup-setup-failure-release.md"
SIGNUP_TIMEOUT_PLAN_PATH = "docs/plans/2026-06-15-signup-timeout-release.md"
RETRYABLE_SIGNUP_FEEDBACK_PLAN_PATH = "docs/plans/2026-06-15-retryable-signup-failure-feedback.md"
SEMANTIC_SIGNUP_SUBMIT_PLAN_PATH = "docs/plans/2026-06-15-semantic-signup-submit-control.md"
SIGNUP_NETWORK_FAILURE_PLAN_PATH = "docs/plans/2026-06-16-signup-network-failure-release.md"
SIGNUP_REQUEST_OWNERSHIP_PLAN_PATH = "docs/plans/2026-06-16-signup-request-ownership.md"
SIGNUP_SUBMIT_BUSY_STATE_PLAN_PATH = "docs/plans/2026-06-17-signup-submit-busy-state.md"
LINEAR_EMAIL_SHAPE_PLAN_PATH = "docs/plans/2026-06-18-linear-email-shape-validation.md"
DEBUG_TRACE_PLAN_PATH = "docs/plans/2026-06-18-debug-trace-response-hardening.md"
TORNADO_SURFACE_PLAN_PATH = "docs/plans/2026-06-20-vendored-tornado-surface-containment.md"


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
        ".github/CODEOWNERS",
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
        CI_PLAN_PATH,
        IDEMPOTENT_SIGNUP_PLAN_PATH,
        HOSTED_VALIDATION_PLAN_PATH,
        SIGNUP_BODY_LIMIT_PLAN_PATH,
        CHECKOUT_CREDENTIAL_PLAN_PATH,
        DATASTORE_LOCAL_DEVELOPMENT_PLAN_PATH,
        LOCATION_INDEPENDENT_MAKE_PLAN_PATH,
        SIGNUP_IN_FLIGHT_PLAN_PATH,
        SIGNUP_SETUP_FAILURE_PLAN_PATH,
        SIGNUP_TIMEOUT_PLAN_PATH,
        RETRYABLE_SIGNUP_FEEDBACK_PLAN_PATH,
        SEMANTIC_SIGNUP_SUBMIT_PLAN_PATH,
        SIGNUP_NETWORK_FAILURE_PLAN_PATH,
        SIGNUP_REQUEST_OWNERSHIP_PLAN_PATH,
        SIGNUP_SUBMIT_BUSY_STATE_PLAN_PATH,
        LINEAR_EMAIL_SHAPE_PLAN_PATH,
        DEBUG_TRACE_PLAN_PATH,
        TORNADO_SURFACE_PLAN_PATH,
        "scripts/check-baseline.py",
        "tests/test_debug_trace_policy.py",
        "tests/test_vendored_tornado_surface.py",
    ]
    for path in required:
        require((ROOT / path).is_file(), f"required file missing: {path}", failures)
    for path in sorted(
        value for name, value in globals().items() if name.endswith("_PLAN_PATH")
    ):
        require(path in required, f"plan path missing from required list: {path}", failures)

    for path in ["next/server.py", "next/base.py", "scripts/check-baseline.py"]:
        try:
            ast.parse(read(path), filename=path)
        except SyntaxError as error:
            failures.append(f"{path} must parse as Python: {error}")

    server = read("next/server.py")
    require("EMAIL_RE" not in server and "normalize_email" in server and "is_valid_email" in server,
            "signup route must validate and normalize email addresses", failures)
    email_shape = server.split("def has_valid_email_shape(email):", 1)[1].split(
        "def has_valid_email_dots", 1
    )[0]
    email_validation = server.split("def is_valid_email(email):", 1)[1].split(
        "class SignUp", 1
    )[0]
    require(
        'parts = email.split("@")' in email_shape
        and "if len(parts) != 2:" in email_shape
        and "local, domain = parts" in email_shape
        and 'return bool(local and domain and "." in domain)' in email_shape
        and "and has_valid_email_shape(email)" in email_validation,
        "signup route must use linear overall email shape validation",
        failures,
    )
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
            "self.send_error(413)" in signup_post,
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
    require("self.send_error(400)" in server,
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
    require("for='email'" in template and ">Email address<" in template,
            "signup email input must have an associated label", failures)
    require("autocomplete='email'" in template and "spellcheck='false'" in template,
            "signup email input must expose email autocomplete and disable spellcheck", failures)
    submit_control = template.split("<td>", 2)[-1].split("</td>", 1)[0]
    require("<button type='submit' id='invite-submit' class='BigButton BlueButton'>" in submit_control and
            "<strong>Request Invitation</strong>" in submit_control and
            "onclick=" not in submit_control and
            "href=" not in submit_control and
            "<a " not in submit_control,
            "signup action must use one semantic submit button without a direct click handler", failures)
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
    form_end_index = template.find("</form>")
    feedback_markup_index = template.find("id='signup-feedback'")
    signup_container_end_index = template.find("</div>", feedback_markup_index)
    require("id='signup-feedback'" in template and
            "role='alert'" in template and
            "aria-atomic='true'" in template and
            0 <= form_end_index < feedback_markup_index < signup_container_end_index,
            "signup form must keep a dedicated accessible feedback region inside its container", failures)
    failure_renderer = template.split("function show_signup_failure()", 1)[1].split("function request_invite(event)", 1)[0]
    require("set_text('signup-feedback', 'Please enter a valid email address.')" in failure_renderer and
            "set_text('signup'," not in failure_renderer,
            "signup failure renderer must update only the dedicated feedback region", failures)
    retryable_failure_helper = template.split("function release_signup_for_retry(request)", 1)[1].split("var invite_request_in_flight", 1)[0]
    helper_identity_index = retryable_failure_helper.find("if (active_invite_request !== request)")
    helper_ownership_clear_index = retryable_failure_helper.find("active_invite_request = null")
    helper_in_flight_clear_index = retryable_failure_helper.find("invite_request_in_flight = false")
    helper_submit_enable_index = retryable_failure_helper.find(
        "document.getElementById('invite-submit').disabled = false"
    )
    helper_feedback_index = retryable_failure_helper.find("show_signup_failure()")
    require(0 <= helper_identity_index < helper_ownership_clear_index < helper_in_flight_clear_index < helper_submit_enable_index < helper_feedback_index,
            "retryable signup failure helper must verify ownership before restoring submit state and feedback", failures)
    request_invite = template.split("function request_invite(event)", 1)[1].split("</script>", 1)[0]
    in_flight_guard_index = request_invite.find("if (invite_request_in_flight)")
    in_flight_start_index = request_invite.find("invite_request_in_flight = true")
    feedback_clear_index = request_invite.find("set_text('signup-feedback', '')")
    request_null_index = request_invite.find("var request = null")
    initial_owner_index = request_invite.find("active_invite_request = request", request_null_index)
    request_create_index = request_invite.find("new XMLHttpRequest()")
    request_owner_index = request_invite.find("active_invite_request = request", request_create_index)
    submit_disable_index = request_invite.find(
        "document.getElementById('invite-submit').disabled = true"
    )
    request_open_index = request_invite.find("request.open('POST', '/signup', true)")
    setup_try_index = request_invite.find("try {")
    timeout_assignment_index = request_invite.find("request.timeout = signup_request_timeout_ms")
    completion_index = request_invite.find("if (request.readyState !== 4)")
    callback_identity_index = request_invite.find("if (active_invite_request !== request)", completion_index)
    success_index = request_invite.find("if (request.status >= 200 && request.status < 300)")
    success_owner_clear_index = request_invite.find("active_invite_request = null", success_index)
    success_in_flight_clear_index = request_invite.find("invite_request_in_flight = false", success_index)
    success_render_index = request_invite.find("set_display('inviteform', 'none')", success_index)
    success_return_index = request_invite.find("return;", success_index)
    failure_release_index = request_invite.find("release_signup_for_retry(request)", success_return_index)
    shared_handler_index = request_invite.find("function release_current_signup_for_retry()")
    shared_handler_release_index = request_invite.find("release_signup_for_retry(request)", shared_handler_index)
    timeout_handler_index = request_invite.find("request.ontimeout = release_current_signup_for_retry")
    network_error_handler_index = request_invite.find("request.onerror = release_current_signup_for_retry")
    abort_handler_index = request_invite.find("request.onabort = release_current_signup_for_retry")
    request_send_index = request_invite.find("request.send(")
    setup_catch_index = request_invite.find("} catch (error)")
    setup_release_index = request_invite.find("release_signup_for_retry(request)", setup_catch_index)
    require("var invite_request_in_flight = false;" in template and
            "var active_invite_request = null;" in template and
            0 <= in_flight_guard_index < in_flight_start_index < request_create_index,
            "signup JavaScript must reject overlapping requests before XHR setup", failures)
    require(0 <= in_flight_start_index < feedback_clear_index < request_null_index < initial_owner_index < setup_try_index < request_create_index < request_owner_index < submit_disable_index < request_open_index,
            "accepted signup retries must acquire ownership and disable submit before XHR setup", failures)
    require(0 <= completion_index < callback_identity_index < success_index < success_owner_clear_index < success_in_flight_clear_index < success_render_index < success_return_index < failure_release_index,
            "completed signup callbacks must verify ownership and clear it before terminal success or failure", failures)
    require(0 <= in_flight_start_index < setup_try_index < request_create_index and
            0 <= request_send_index < setup_catch_index < setup_release_index,
            "signup JavaScript must delegate synchronous setup failures for retry", failures)
    require("var signup_request_timeout_ms = 10000;" in template and
            0 <= request_open_index < timeout_assignment_index < timeout_handler_index < request_send_index,
            "signup JavaScript must install the finite request timeout before dispatch", failures)
    require(0 <= failure_release_index < shared_handler_index < shared_handler_release_index < timeout_handler_index < network_error_handler_index < abort_handler_index < request_send_index,
            "signup JavaScript must install timeout, network-error, and abort release handlers before dispatch", failures)
    require(request_invite.count("release_signup_for_retry(request)") == 3 and
            request_invite.count("invite_request_in_flight = false") == 1 and
            "show_signup_failure()" not in request_invite,
            "all retryable request failures must remain request-bound through the shared release helper", failures)
    require("set_text('signup-feedback', 'Please enter a valid email address.')" not in request_invite and
            "set_text('signup', 'Please enter a valid email address.')" not in request_invite and
            "disabled = false" not in request_invite and
            "set_text('signup', \"Thank You - we will review your application" in request_invite,
            "retryable failures must restore submit state while success remains terminal", failures)

    style = read("next/static/style.css")
    big_button_style = style.split(".BigButton {", 1)[1].split("}", 1)[0]
    disabled_button_marker = ".BigButton:disabled {"
    disabled_button_style = style.partition(disabled_button_marker)[2].partition("}")[0]
    require("font-family: inherit;" in big_button_style and
            "cursor: pointer;" in big_button_style,
            "semantic signup button must retain inherited typography and pointer affordance", failures)
    require(disabled_button_marker in style and
            "cursor: wait;" in disabled_button_style and
            "opacity: 0.6;" in disabled_button_style,
            "disabled signup button must expose a visible busy-state affordance", failures)
    require("http://s3.amazonaws.com" not in style, "background asset URL must use HTTPS", failures)

    app_yaml = read("next/app.yaml")
    require("runtime: python" in app_yaml and "script: server.py" in app_yaml,
            "App Engine runtime and script mapping must stay documented", failures)
    require(app_yaml.count("secure: always") >= 4,
            "all App Engine handlers must require secure transport", failures)

    makefile = read("Makefile")
    require(makefile == EXPECTED_MAKEFILE,
            "Makefile must exactly preserve rooted dependency-free aliases and the Python override",
            failures)

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
        require(module.has_valid_email_shape("user@example.com"),
                "valid email shape must be accepted", failures)
        require(not module.has_valid_email_shape("user@@example.com"),
                "multiple email separators must be rejected", failures)
        require(not module.has_valid_email_shape("@example.com"),
                "blank email local part must be rejected", failures)
        require(not module.has_valid_email_shape("user@"),
                "blank email domain must be rejected", failures)
        require(not module.has_valid_email_shape("user@example"),
                "email domain without a dot must be rejected", failures)
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
        require(not module.is_valid_email("user@@example.com"),
                "email with multiple separators must be rejected", failures)
        require(not module.is_valid_email("user@example"),
                "email without a dotted domain must be rejected", failures)
        require(not module.is_valid_email("not-an-email"), "invalid email must be rejected", failures)
    except Exception as error:
        failures.append(f"server helper contracts failed: {error}")

    readme_source = read("README.md")
    vision_source = read("VISION.md")
    security_source = read("SECURITY.md")
    changes_source = read("CHANGES.md")
    docs = readme_source + "\n" + vision_source + "\n" + security_source
    location_independent_make_plan = read(LOCATION_INDEPENDENT_MAKE_PLAN_PATH)
    require("make -f /path/to/nextinvite.com/Makefile check" in readme_source,
            "README must document location-independent Makefile invocation", failures)
    require(all(evidence in location_independent_make_plan.lower() for evidence in [
        "status: completed",
        "root and external-directory",
        "six isolated hostile mutations",
    ]),
            "location-independent Make plan must record completed root, external, and mutation verification",
            failures)
    for phrase in ["make lint", "make test", "make build", "make check", "GitHub Actions", "datastore", "private user data"]:
        require(phrase.lower() in docs.lower(), f"docs must mention {phrase}", failures)
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
    require("signup in-flight guard" in docs.lower(),
            "docs must mention the signup in-flight guard", failures)
    require("signup request timeout release" in docs.lower(),
            "docs must mention the signup request timeout release", failures)
    require("semantic signup submit control" in docs.lower(),
            "docs must mention the semantic signup submit control", failures)
    guidance_sources = {
        "README.md": readme_source,
        "SECURITY.md": security_source,
        "VISION.md": vision_source,
        "CHANGES.md": changes_source,
    }
    for relative_path, guidance_source in guidance_sources.items():
        require("retryable signup feedback" in guidance_source.lower(),
                f"{relative_path} must document retryable signup feedback", failures)
        require("signup network failure release" in guidance_source.lower(),
                f"{relative_path} must document signup network failure release", failures)
        require("signup request ownership" in guidance_source.lower(),
                f"{relative_path} must document signup request ownership", failures)
        require("signup submit busy state" in guidance_source.lower(),
                f"{relative_path} must document signup submit busy state", failures)
        require("linear email shape validation" in guidance_source.lower(),
                f"{relative_path} must document linear email shape validation", failures)
    readme = " ".join(read("README.md").split())
    for phrase in [
        "`SignUp` is the only application datastore entity",
        "`email` `db.TextProperty`",
        "`added` `db.DateTimeProperty`",
        "signup-<sha256>",
        "not encryption",
        "stored as plaintext private data",
        "retired Python 2 App Engine standard environment",
        "dev_appserver.py next/app.yaml",
        "appcfg.py update next/",
        "deployment is not verified",
        "Keep local datastore files, datastore exports",
    ]:
        require(phrase in readme,
                f"README datastore guidance must mention {phrase}", failures)
    security = " ".join(security_source.split())
    for phrase in [
        "stores normalized email as plaintext private data",
        "provides retry idempotency, not encryption",
        "Keep local datastore files and exports out of git",
        "do not deploy without an owned App Engine project",
    ]:
        require(phrase in security,
                f"security datastore guidance must mention {phrase}", failures)
    vision = " ".join(vision_source.split())
    for phrase in [
        "normalized plaintext email",
        "idempotency, not encryption",
        "historical and unverified",
        "local datastore files, exports, credentials",
    ]:
        require(phrase in vision,
                f"vision datastore guidance must mention {phrase}", failures)
    changes = changes_source
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
    require("signup in-flight guard" in changes.lower(),
            "CHANGES must mention the signup in-flight guard", failures)
    require("signup request timeout release" in changes.lower(),
            "CHANGES must mention the signup request timeout release", failures)
    require("semantic signup submit control" in changes.lower(),
            "CHANGES must mention the semantic signup submit control", failures)
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
    ci_plan = read(CI_PLAN_PATH) if (ROOT / CI_PLAN_PATH).is_file() else ""
    require("status: completed" in ci_plan and "scripts/check-baseline.py" in ci_plan,
            "CI baseline plan must record status and active checker", failures)
    signup_in_flight_plan = read(SIGNUP_IN_FLIGHT_PLAN_PATH)
    signup_in_flight_verification = markdown_section(
        signup_in_flight_plan, "Verification Completed"
    )
    require("status: completed" in signup_in_flight_plan and
            "All four Make gates passed" in signup_in_flight_verification and
            "Six isolated hostile mutations were rejected" in signup_in_flight_verification and
            "external directory" in signup_in_flight_verification and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", signup_in_flight_verification),
            "signup in-flight guard plan must record completed verification", failures)
    signup_setup_failure_plan = read(SIGNUP_SETUP_FAILURE_PLAN_PATH)
    signup_setup_failure_verification = markdown_section(
        signup_setup_failure_plan, "Verification Completed"
    )
    require("status: completed" in signup_setup_failure_plan.lower() and
            "All four Make gates passed" in signup_setup_failure_verification and
            "Six isolated hostile mutations were rejected" in signup_setup_failure_verification and
            "external directory" in signup_setup_failure_verification and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", signup_setup_failure_verification),
            "signup setup failure release plan must record completed verification", failures)
    signup_timeout_plan = read(SIGNUP_TIMEOUT_PLAN_PATH)
    signup_timeout_verification = markdown_section(
        signup_timeout_plan, "Verification Completed"
    )
    require("status: completed" in signup_timeout_plan.lower() and
            "All four Make gates passed" in signup_timeout_verification and
            "Seven isolated hostile mutations were rejected" in signup_timeout_verification and
            "external directory" in signup_timeout_verification and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", signup_timeout_verification),
            "signup request timeout release plan must record completed verification", failures)
    retryable_feedback_plan = read(RETRYABLE_SIGNUP_FEEDBACK_PLAN_PATH)
    retryable_feedback_verification = markdown_section(
        retryable_feedback_plan, "Verification Completed"
    )
    require("status: completed" in retryable_feedback_plan.lower() and
            "All four Make gates passed" in retryable_feedback_verification and
            "Nine isolated hostile mutations were rejected" in retryable_feedback_verification and
            "external directory" in retryable_feedback_verification and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", retryable_feedback_verification),
            "retryable signup feedback plan must record completed verification", failures)
    semantic_submit_plan = read(SEMANTIC_SIGNUP_SUBMIT_PLAN_PATH)
    semantic_submit_verification = markdown_section(
        semantic_submit_plan, "Verification Completed"
    )
    require("status: completed" in semantic_submit_plan.lower() and
            "All four Make gates passed" in semantic_submit_verification and
            "Seven isolated hostile mutations were rejected" in semantic_submit_verification and
            "external directory" in semantic_submit_verification and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", semantic_submit_verification),
            "semantic signup submit control plan must record completed verification", failures)
    network_failure_plan = read(SIGNUP_NETWORK_FAILURE_PLAN_PATH)
    network_failure_verification = markdown_section(
        network_failure_plan, "Verification Completed"
    )
    require("status: completed" in network_failure_plan.lower() and
            "All four Make gates passed" in network_failure_verification and
            "Ten isolated hostile mutations were rejected" in network_failure_verification and
            "external directory" in network_failure_verification and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", network_failure_verification),
            "signup network failure release plan must record completed verification", failures)
    request_ownership_plan = read(SIGNUP_REQUEST_OWNERSHIP_PLAN_PATH)
    request_ownership_verification = markdown_section(
        request_ownership_plan, "Verification Completed"
    )
    require("status: completed" in request_ownership_plan.lower() and
            "All four Make gates passed" in request_ownership_verification and
            "Eight isolated hostile mutations were rejected" in request_ownership_verification and
            "external directory" in request_ownership_verification and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", request_ownership_verification),
            "signup request ownership plan must record completed verification", failures)
    submit_busy_state_plan = read(SIGNUP_SUBMIT_BUSY_STATE_PLAN_PATH)
    submit_busy_state_verification = markdown_section(
        submit_busy_state_plan, "Verification Completed"
    )
    require("status: completed" in submit_busy_state_plan.lower() and
            "All four Make gates passed" in submit_busy_state_verification and
            "Nine isolated hostile mutations were rejected" in submit_busy_state_verification and
            "external directory" in submit_busy_state_verification and
            "browser" in submit_busy_state_verification and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", submit_busy_state_verification),
            "signup submit busy state plan must record completed verification", failures)
    linear_email_shape_plan = read(LINEAR_EMAIL_SHAPE_PLAN_PATH)
    linear_email_shape_verification = markdown_section(
        linear_email_shape_plan, "Verification Completed"
    )
    require("status: completed" in linear_email_shape_plan.lower() and
            "All four Make gates passed" in linear_email_shape_verification and
            "Eight isolated hostile mutations were rejected" in linear_email_shape_verification and
            "external directory" in linear_email_shape_verification and
            "CodeQL" in linear_email_shape_verification and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", linear_email_shape_verification),
            "linear email shape validation plan must record completed verification", failures)
    idempotent_signup_plan = read(IDEMPOTENT_SIGNUP_PLAN_PATH) if (ROOT / IDEMPOTENT_SIGNUP_PLAN_PATH).is_file() else ""
    require("status: completed" in idempotent_signup_plan and "make check" in idempotent_signup_plan,
            "idempotent signup key plan must record status and verification", failures)
    datastore_local_development_plan = read(DATASTORE_LOCAL_DEVELOPMENT_PLAN_PATH)
    require(
        "status: completed" in datastore_local_development_plan
        and "make check" in datastore_local_development_plan
        and "hostile mutations rejected" in datastore_local_development_plan,
        "datastore local development plan must record completed verification",
        failures,
    )
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
    workflow_files = [
        *sorted((ROOT / ".github/workflows").glob("*.yml")),
        *sorted((ROOT / ".github/workflows").glob("*.yaml")),
    ]
    codeowners = read(".github/CODEOWNERS")
    require("status: completed" in hosted_plan and "make check" in hosted_plan,
            "hosted static validation plan must record status and verification", failures)
    for expected in [
        "permissions:\n  contents: read",
        "cancel-in-progress: true",
        "runs-on: ubuntu-24.04",
        "timeout-minutes: 10",
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
        "persist-credentials: false",
        "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
        'python-version: "3.12"',
        "run: make check",
    ]:
        require(expected in workflow, f"Check workflow must keep {expected}", failures)
    workflow_files = sorted(str(path.relative_to(ROOT)) for path in (ROOT / ".github/workflows").rglob("*") if path.is_file())
    require(workflow_files == [".github/workflows/check.yml"], "check.yml must be the repository's only hosted workflow", failures)
    require(codeowners.strip() == "* @garethpaul", "CODEOWNERS must assign the repository to @garethpaul", failures)

    checkout_action = (
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10"
    )
    checkout_blocks = re.findall(
        rf"(?m)^(?P<indent> *)- +uses: +{re.escape(checkout_action)}[^\n]*\n"
        rf"(?P=indent)  with:\n"
        rf"(?P=indent)    persist-credentials: +false *$",
        workflow,
    )
    checkout_actions = re.findall(
        r"(?m)^\s*-\s+uses:\s+actions/checkout@",
        workflow,
    )
    require(
        len(workflow_files) == 1
        and workflow.count("permissions:") == 1
        and workflow.count("contents: read") == 1
        and not re.search(r"(?m)^\s*[A-Za-z-]+:\s*write\s*$", workflow)
        and len(checkout_actions) == 1
        and workflow.count(checkout_action) == 1
        and len(checkout_blocks) == 1
        and workflow.count("persist-credentials: false") == 1
        and "persist-credentials: true" not in workflow,
        "Check workflow must keep one read-only permission block and one "
        "pinned, credential-free checkout",
        failures,
    )

    checkout_plan = read(CHECKOUT_CREDENTIAL_PLAN_PATH) if (ROOT / CHECKOUT_CREDENTIAL_PLAN_PATH).is_file() else ""
    checkout_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", checkout_plan)
    checkout_work = markdown_section(checkout_plan, "Work Completed")
    checkout_verification = markdown_section(checkout_plan, "Verification Completed")
    require(
        checkout_status == ["completed"]
        and bool(checkout_work)
        and "make check" in checkout_verification,
        "checkout credential plan must record one completed status, completed "
        "work, and make check verification",
        failures,
    )

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("nextinvite baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
