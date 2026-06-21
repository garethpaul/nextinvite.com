#!/usr/bin/env python3
"""Synthetic smoke and structural contracts for the legacy Tornado WSGI subset."""

from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
TORNADO_ROOT = ROOT / "next" / "tornado"
NEXT_ROOT = ROOT / "next"
WEB_SOURCE = TORNADO_ROOT / "web.py"
ALLOWED_MODULES = {
    "__init__.py",
    "escape.py",
    "httputil.py",
    "locale.py",
    "stack_context.py",
    "template.py",
    "util.py",
    "web.py",
    "wsgi.py",
}


class VendoredTornadoSurfaceTest(unittest.TestCase):
    def run_converted_smoke(self, source, copy_application=False):
        with tempfile.TemporaryDirectory(prefix="nextinvite-tornado-") as directory:
            converted_root = Path(directory)
            if copy_application:
                shutil.copytree(NEXT_ROOT, converted_root / "next")
                tornado_path = converted_root / "next" / "tornado"
                pythonpath = os.pathsep.join([
                    str(converted_root / "next"),
                    str(converted_root),
                ])
            else:
                shutil.copytree(TORNADO_ROOT, converted_root / "tornado")
                tornado_path = converted_root / "tornado"
                pythonpath = str(converted_root)

            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "lib2to3",
                    "-w",
                    "-n",
                    str(tornado_path),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            environment = os.environ.copy()
            environment["PYTHONPATH"] = pythonpath
            completed = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    textwrap.dedent(source),
                ],
                env=environment,
                capture_output=True,
                text=True,
            )
            if completed.returncode != 0:
                self.fail(
                    "converted smoke failed\nSTDOUT:\n%s\nSTDERR:\n%s" % (
                        completed.stdout,
                        completed.stderr,
                    )
                )

    def test_converted_synthetic_wsgi_smoke_serves_write_response(self):
        self.run_converted_smoke(
            """
            import io
            import tornado.web
            import tornado.wsgi

            class Handler(tornado.web.RequestHandler):
                def get(self):
                    self.write("ok")

            app = tornado.wsgi.WSGIApplication([(r"/", Handler)], debug=False)
            status = []

            def start_response(value, headers):
                status.append(value)

            environ = {
                "REQUEST_METHOD": "GET",
                "SCRIPT_NAME": "",
                "PATH_INFO": "/",
                "QUERY_STRING": "",
                "REMOTE_ADDR": "127.0.0.1",
                "SERVER_NAME": "localhost",
                "SERVER_PORT": "80",
                "SERVER_PROTOCOL": "HTTP/1.1",
                "HTTP_HOST": "localhost",
                "wsgi.version": (1, 0),
                "wsgi.url_scheme": "http",
                "wsgi.input": io.BytesIO(b""),
                "wsgi.errors": io.StringIO(),
                "wsgi.multithread": False,
                "wsgi.multiprocess": False,
                "wsgi.run_once": False,
            }
            body = b"".join(app(environ, start_response))
            assert status == ["200 OK"], status
            assert body == b"ok", body
            """
        )

    def test_converted_synthetic_wsgi_smoke_preserves_finish_chunk_compatibility(self):
        self.run_converted_smoke(
            """
            import io
            import tornado.web
            import tornado.wsgi

            class Handler(tornado.web.RequestHandler):
                def get(self):
                    self.finish("ok")

            app = tornado.wsgi.WSGIApplication([(r"/", Handler)], debug=False)
            status = []

            def start_response(value, headers):
                status.append(value)

            environ = {
                "REQUEST_METHOD": "GET",
                "SCRIPT_NAME": "",
                "PATH_INFO": "/",
                "QUERY_STRING": "",
                "REMOTE_ADDR": "127.0.0.1",
                "SERVER_NAME": "localhost",
                "SERVER_PORT": "80",
                "SERVER_PROTOCOL": "HTTP/1.1",
                "HTTP_HOST": "localhost",
                "wsgi.version": (1, 0),
                "wsgi.url_scheme": "http",
                "wsgi.input": io.BytesIO(b""),
                "wsgi.errors": io.StringIO(),
                "wsgi.multithread": False,
                "wsgi.multiprocess": False,
                "wsgi.run_once": False,
            }
            body = b"".join(app(environ, start_response))
            assert status == ["200 OK"], status
            assert body == b"ok", body
            """
        )

    def test_converted_synthetic_wsgi_smoke_exercises_active_routes(self):
        self.run_converted_smoke(
            """
            import cgi
            import io
            import sys
            import types
            import urllib.parse

            cgi.parse_qs = urllib.parse.parse_qs

            saved_signups = []

            markdown = types.ModuleType("markdown")
            google = types.ModuleType("google")
            appengine = types.ModuleType("google.appengine")
            api = types.ModuleType("google.appengine.api")
            users = types.ModuleType("google.appengine.api.users")
            ext = types.ModuleType("google.appengine.ext")
            db = types.ModuleType("google.appengine.ext.db")

            google.appengine = appengine
            appengine.api = api
            appengine.ext = ext
            api.users = users
            ext.db = db

            users.get_current_user = lambda: None
            users.is_current_user_admin = lambda: False
            users.create_login_url = lambda uri: "/login?next=" + uri

            class Model:
                def __init__(self, key_name=None, **kwargs):
                    self.key_name = key_name

                def put(self):
                    saved_signups.append({
                        "key_name": self.key_name,
                        "email": self.email,
                    })

            db.Model = Model
            db.TextProperty = lambda *args, **kwargs: None
            db.DateTimeProperty = lambda *args, **kwargs: None

            sys.modules.update({
                "markdown": markdown,
                "google": google,
                "google.appengine": appengine,
                "google.appengine.api": api,
                "google.appengine.api.users": users,
                "google.appengine.ext": ext,
                "google.appengine.ext.db": db,
            })

            import server

            routes = [
                (spec.regex.pattern, spec.handler_class.__name__)
                for _, handlers in server.application.handlers
                for spec in handlers
            ]
            assert routes == [("/$", "HomeHandler"), ("/signup$", "SignUpHandler")], routes
            assert server.application.settings["debug"] is False
            assert server.application.settings["xsrf_cookies"] is True

            def request(method, path, body="", extra_headers=None):
                status = []
                response_headers = []

                def start_response(value, headers):
                    status.append(value)
                    response_headers.extend(headers)

                environ = {
                    "REQUEST_METHOD": method,
                    "SCRIPT_NAME": "",
                    "PATH_INFO": path,
                    "QUERY_STRING": "",
                    "REMOTE_ADDR": "127.0.0.1",
                    "SERVER_NAME": "localhost",
                    "SERVER_PORT": "80",
                    "SERVER_PROTOCOL": "HTTP/1.1",
                    "HTTP_HOST": "localhost",
                    "HTTP_COOKIE": "_xsrf=legacy-token",
                    "wsgi.version": (1, 0),
                    "wsgi.url_scheme": "http",
                    "wsgi.input": io.StringIO(body),
                    "wsgi.errors": io.StringIO(),
                    "wsgi.multithread": False,
                    "wsgi.multiprocess": False,
                    "wsgi.run_once": False,
                }
                if body:
                    environ["CONTENT_TYPE"] = (
                        "application/x-www-form-urlencoded; charset=UTF-8"
                    )
                    environ["CONTENT_LENGTH"] = str(len(body))
                for name, value in (extra_headers or {}).items():
                    environ["HTTP_" + name.upper().replace("-", "_")] = value

                response = b"".join(server.application(environ, start_response))
                return status[0], response_headers, response

            home_status, _, home_body = request("GET", "/")
            assert home_status == "200 OK", home_status
            assert b"Next Invite" in home_body, home_body
            assert b'name="_xsrf"' in home_body, home_body
            assert b'value="legacy-token"' in home_body, home_body

            signup_status, _, signup_body = request(
                "POST",
                "/signup",
                "_xsrf=legacy-token&email=User%40Example.COM",
            )
            assert signup_status == "200 OK", signup_status
            assert signup_body == b"ok", signup_body
            assert saved_signups == [{
                "key_name": server.signup_key_name("user@example.com"),
                "email": "user@example.com",
            }], saved_signups
            """
            ,
            copy_application=True,
        )

    def test_make_check_runs_surface_contract(self):
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertIn(
            '$(PYTHON) "$(ROOT)/tests/test_vendored_tornado_surface.py"',
            makefile,
        )

    def test_maintenance_docs_state_wsgi_only_boundary(self):
        for relative_path in ("README.md", "SECURITY.md", "VISION.md"):
            content = (ROOT / relative_path).read_text(encoding="utf-8")
            normalized_content = " ".join(content.split())
            self.assertIn("WSGI-only Tornado subset", content, relative_path)
            self.assertIn(
                "synthetic converted WSGI smoke",
                normalized_content,
                relative_path,
            )
            self.assertIn(
                "does not prove Python 3 App Engine compatibility",
                normalized_content,
                relative_path,
            )

    def test_package_is_limited_to_wsgi_import_closure(self):
        modules = {path.name for path in TORNADO_ROOT.glob("*.py")}
        self.assertEqual(ALLOWED_MODULES, modules)
        self.assertFalse((TORNADO_ROOT / "platform").exists())

    def test_non_executed_upstream_test_suite_is_absent(self):
        self.assertFalse((TORNADO_ROOT / "test").exists())

    def test_finish_keeps_legacy_chunk_api_but_internal_calls_stay_explicit(self):
        source = WEB_SOURCE.read_text(encoding="utf-8")
        self.assertIn("    def finish(self, chunk=None):", source)
        self.assertIn("        if chunk is not None: self.write(chunk)", source)

        calls = re.findall(r"self\.finish\(([^)]*)\)", source)
        self.assertEqual([], [argument for argument in calls if argument.strip()])

    def test_preserved_wsgi_subset_has_no_removed_runtime_hooks(self):
        web_source = WEB_SOURCE.read_text(encoding="utf-8")
        wsgi_source = (TORNADO_ROOT / "wsgi.py").read_text(encoding="utf-8")

        self.assertNotIn("from tornado import autoreload", web_source)
        self.assertNotIn("from tornado.httpserver import HTTPServer", web_source)
        self.assertNotIn("class WSGIContainer", wsgi_source)


if __name__ == "__main__":
    unittest.main()
