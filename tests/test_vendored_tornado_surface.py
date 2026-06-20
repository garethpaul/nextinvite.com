#!/usr/bin/env python3
"""Structural contracts for the preserved Tornado WSGI subset."""

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
    def test_converted_subset_serves_wsgi_request(self):
        with tempfile.TemporaryDirectory(prefix="nextinvite-tornado-") as directory:
            converted_root = Path(directory)
            shutil.copytree(TORNADO_ROOT, converted_root / "tornado")
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "lib2to3",
                    "-w",
                    "-n",
                    str(converted_root / "tornado"),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(converted_root)
            subprocess.run(
                [
                    sys.executable,
                    "-c",
                    textwrap.dedent(
                        """
                        import io
                        import tornado.web
                        import tornado.wsgi

                        class Handler(tornado.web.RequestHandler):
                            def get(self):
                                self.write("ok")

                        app = tornado.wsgi.WSGIApplication(
                            [(r"/", Handler)], debug=False
                        )
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
                    ),
                ],
                check=True,
                env=environment,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
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
            self.assertIn("WSGI-only Tornado subset", content, relative_path)

    def test_package_is_limited_to_wsgi_import_closure(self):
        modules = {path.name for path in TORNADO_ROOT.glob("*.py")}
        self.assertEqual(ALLOWED_MODULES, modules)
        self.assertFalse((TORNADO_ROOT / "platform").exists())

    def test_non_executed_upstream_test_suite_is_absent(self):
        self.assertFalse((TORNADO_ROOT / "test").exists())

    def test_finish_has_no_implicit_response_body(self):
        source = WEB_SOURCE.read_text(encoding="utf-8")
        self.assertIn("    def finish(self):", source)
        self.assertNotIn("    def finish(self, chunk=None):", source)

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
