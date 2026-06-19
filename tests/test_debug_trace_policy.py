#!/usr/bin/env python3
"""Behavior contracts for legacy Tornado error handling."""

from pathlib import Path
from lib2to3.refactor import RefactoringTool, get_fixers_from_package
import importlib.util
import os
import sys
import textwrap
import types
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
WEB_SOURCE = ROOT / "next" / "tornado" / "web.py"
SENTINEL = "private-debug-trace-sentinel"


def extract_method(name):
    lines = WEB_SOURCE.read_text(encoding="utf-8").splitlines()
    marker = "    def %s(" % name
    matches = [index for index, line in enumerate(lines) if line.startswith(marker)]
    if len(matches) != 1:
        raise AssertionError("expected exactly one %s method" % name)
    start = matches[0]
    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if line.startswith("    def ") or line.startswith("    @"):
            end = index
            break
    return textwrap.dedent("\n".join(lines[start:end]))


class CapturingLogging:
    def __init__(self):
        self.records = []

    def error(self, *args, **kwargs):
        self.records.append((args, kwargs, sys.exc_info()))

    def warning(self, *args, **kwargs):
        self.records.append((args, kwargs, sys.exc_info()))


def load_handler_class(logging_module):
    methods = [
        extract_method("send_error"),
        extract_method("write_error"),
        extract_method("_request_summary"),
        extract_method("_handle_request_exception"),
    ]
    class_source = """
class Handler(object):
    def __init__(self, debug):
        self.settings = {"debug": debug}
        self.request = type("Request", (), {
            "method": "GET",
            "uri": "/failure",
            "remote_ip": "127.0.0.1",
        })()
        self._headers_written = False
        self._finished = False
        self._write_buffer = []
        self.headers = {}
        self.status_code = 200

    def clear(self):
        self._write_buffer = []
        self.headers = {}

    def set_status(self, status_code):
        self.status_code = status_code

    def set_header(self, name, value):
        self.headers[name] = value

    def write(self, chunk):
        self._write_buffer.append(chunk)

    def finish(self, chunk=None):
        if chunk is not None:
            self.write(chunk)
        self._finished = True

%s
""" % "\n\n".join(textwrap.indent(method, "    ") for method in methods)
    tool = RefactoringTool(get_fixers_from_package("lib2to3.fixes"))
    converted = str(tool.refactor_string(class_source, "legacy_web_handler"))

    class HTTPError(Exception):
        pass

    namespace = {
        "HTTPError": HTTPError,
        "httplib": types.SimpleNamespace(responses={500: "Internal Server Error"}),
        "logging": logging_module,
        "sys": sys,
    }
    exec(compile(converted, "legacy_web_handler", "exec"), namespace)
    return namespace["Handler"]


def exercise_uncaught_exception(debug):
    logging_module = CapturingLogging()
    handler_class = load_handler_class(logging_module)
    handler = handler_class(debug)
    try:
        raise RuntimeError(SENTINEL)
    except RuntimeError as error:
        handler._handle_request_exception(error)
    return handler, logging_module


def load_baseline_module():
    script_path = ROOT / "scripts" / "check-baseline.py"
    spec = importlib.util.spec_from_file_location("nextinvite_baseline", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DebugTraceResponseTest(unittest.TestCase):
    def test_make_check_runs_debug_trace_contract(self):
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

        self.assertIn(
            '$(PYTHON) -W ignore::DeprecationWarning '
            '"$(ROOT)/tests/test_debug_trace_policy.py"',
            makefile,
        )

    def test_debug_response_is_generic(self):
        handler, _ = exercise_uncaught_exception(debug=True)

        response = "".join(handler._write_buffer)
        self.assertEqual(500, handler.status_code)
        self.assertEqual(
            "<html><title>500: Internal Server Error</title>"
            "<body>500: Internal Server Error</body></html>",
            response,
        )
        self.assertNotIn(SENTINEL, response)
        self.assertNotIn("Traceback", response)

    def test_production_response_is_generic(self):
        handler, _ = exercise_uncaught_exception(debug=False)

        response = "".join(handler._write_buffer)
        self.assertNotIn(SENTINEL, response)
        self.assertNotIn("Traceback", response)

    def test_uncaught_exception_remains_in_server_log_context(self):
        _, logging_module = exercise_uncaught_exception(debug=True)

        exception_records = [
            record for record in logging_module.records
            if record[1].get("exc_info") is True
        ]
        self.assertEqual(1, len(exception_records))
        self.assertEqual(SENTINEL, str(exception_records[0][2][1]))

    def test_legacy_environment_cannot_enable_application_debug(self):
        baseline = load_baseline_module()
        with mock.patch.dict(
            os.environ,
            {"SERVER_SOFTWARE": "Development/nextinvite-local"},
            clear=False,
        ):
            server = baseline.load_server_module()

        self.assertIs(False, server.application.settings["debug"])

    def test_security_docs_define_error_and_migration_contract(self):
        documentation = "\n".join(
            (ROOT / path).read_text(encoding="utf-8")
            for path in ("README.md", "SECURITY.md")
        ).lower()

        self.assertIn("http error responses remain generic", documentation)
        self.assertIn("exception details remain in server-side logs", documentation)
        self.assertIn("runtime migration remains p0 before redeployment", documentation)


if __name__ == "__main__":
    unittest.main()
