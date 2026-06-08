#!/usr/bin/env python3
"""Static and dependency-free checks for the NextInvite App Engine sample."""

from pathlib import Path
import ast
import importlib.util
import sys
import types


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = "docs/plans/2026-06-08-nextinvite-baseline.md"


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


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
    require("self.set_status(400)" in server and 'self.write("invalid email")' in server,
            "invalid signup emails must return a deterministic 400", failures)
    require('"xsrf_cookies": True' in server, "XSRF protection must remain enabled", failures)

    template = read("next/templates/home.html")
    require("{% autoescape None %}" not in template,
            "home template must not disable autoescaping", failures)
    require("http://fonts.googleapis.com" not in template, "template font URL must use HTTPS", failures)
    require("type='email'" in template and "required" in template,
            "signup form must use required email input", failures)
    require("request_invite(event)" in template and "event.preventDefault()" in template,
            "signup click handler must receive the click event explicitly", failures)
    require("$.post('/signup'" in template,
            "signup JavaScript must post to the absolute signup route", failures)

    style = read("next/static/style.css")
    require("http://s3.amazonaws.com" not in style, "background asset URL must use HTTPS", failures)

    app_yaml = read("next/app.yaml")
    require("runtime: python" in app_yaml and "script: server.py" in app_yaml,
            "App Engine runtime and script mapping must stay documented", failures)
    require(app_yaml.count("secure: always") >= 4,
            "all App Engine handlers must require secure transport", failures)

    gitignore = read(".gitignore")
    for expected in ["__pycache__/", "*.pyc", ".env", "appengine-generated/", "bulkloader-*"]:
        require(expected in gitignore, f".gitignore must include {expected}", failures)

    try:
        module = load_server_module()
        require(module.normalize_email(" USER@Example.COM ") == "user@example.com",
                "normalize_email must trim and lowercase", failures)
        require(module.is_valid_email("user@example.com"), "valid email must be accepted", failures)
        require(not module.is_valid_email("not-an-email"), "invalid email must be rejected", failures)
    except Exception as error:
        failures.append(f"server helper contracts failed: {error}")

    docs = read("README.md") + "\n" + read("VISION.md") + "\n" + read("SECURITY.md")
    for phrase in ["make check", "datastore", "private user data"]:
        require(phrase in docs.lower(), f"docs must mention {phrase}", failures)

    plan = read(PLAN_PATH)
    require("status: completed" in plan and "Verification" in plan,
            "plan must be completed and include verification", failures)

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("nextinvite baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
