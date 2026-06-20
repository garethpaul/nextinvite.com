#!/usr/bin/env python3
"""Behavior contracts for legacy Tornado error handling."""

from pathlib import Path
from lib2to3.refactor import RefactoringTool, get_fixers_from_package
import importlib.util
import json
import os
import sys
import textwrap
import traceback
import types
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
WEB_SOURCE = ROOT / "next" / "tornado" / "web.py"
SENTINEL = "private-debug-trace-sentinel"
QUERY_SENTINEL = "query-secret@example.com"
BODY_SENTINEL = "body-secret@example.com"
HEADER_SENTINEL = "Bearer private-token"
CAUSE_SENTINEL = "nested-database-secret"


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
        extract_method("_wants_json_error"),
        extract_method("_write_generic_error"),
        extract_method("write_error"),
        extract_method("_request_summary"),
        extract_method("_log_request_error"),
        extract_method("_handle_request_exception"),
    ]
    class_source = """
class Handler(object):
    def __init__(self, debug, accept="text/html"):
        self.settings = {"debug": debug}
        self.request_id = "0123456789abcdef0123456789abcdef"
        self.request = type("Request", (), {
            "method": "GET",
            "path": "/failure",
            "uri": "/failure?email=%%s" %% QUERY_SENTINEL,
            "remote_ip": "127.0.0.1",
            "body": "email=%%s" %% BODY_SENTINEL,
            "headers": {
                "Accept": accept,
                "Authorization": HEADER_SENTINEL,
            },
        })()
        self._headers_written = False
        self._finished = False
        self._write_buffer = []
        self.headers = {}
        self.status_code = 200

    def clear(self):
        self._write_buffer = []
        self.headers = {"X-Request-ID": self.request_id}
        self._finished = False

    def set_status(self, status_code):
        self.status_code = status_code

    def set_header(self, name, value):
        self.headers[name] = value

    def write(self, chunk):
        if isinstance(chunk, dict):
            chunk = escape.json_encode(chunk)
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
        "BODY_SENTINEL": BODY_SENTINEL,
        "HEADER_SENTINEL": HEADER_SENTINEL,
        "HTTPError": HTTPError,
        "QUERY_SENTINEL": QUERY_SENTINEL,
        "escape": types.SimpleNamespace(json_encode=json.dumps),
        "httplib": types.SimpleNamespace(responses={
            400: "Bad Request",
            413: "Request Entity Too Large",
            500: "Internal Server Error",
        }),
        "logging": logging_module,
        "os": os,
        "sys": sys,
        "traceback": traceback,
    }
    exec(compile(converted, "legacy_web_handler", "exec"), namespace)
    return namespace["Handler"]


def exercise_uncaught_exception(debug, accept="text/html", nested=False):
    logging_module = CapturingLogging()
    handler_class = load_handler_class(logging_module)
    handler = handler_class(debug, accept=accept)
    try:
        if nested:
            try:
                raise ValueError(CAUSE_SENTINEL)
            except ValueError as cause:
                raise RuntimeError(SENTINEL) from cause
        raise RuntimeError(SENTINEL)
    except RuntimeError as error:
        handler._handle_request_exception(error)
    return handler, logging_module


def structured_log_records(logging_module):
    records = []
    for args, _, _ in logging_module.records:
        if len(args) == 2 and args[0] == "%s":
            records.append(json.loads(args[1]))
    return records


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
        self.assertEqual(handler.request_id, handler.headers["X-Request-ID"])
        self.assertEqual("no-store", handler.headers["Cache-Control"])

    def test_production_response_is_generic(self):
        handler, _ = exercise_uncaught_exception(debug=False)

        response = "".join(handler._write_buffer)
        self.assertNotIn(SENTINEL, response)
        self.assertNotIn("Traceback", response)

    def test_json_error_schema_is_generic_and_correlated(self):
        handler, _ = exercise_uncaught_exception(
            debug=True,
            accept="text/html;q=0.8, application/problem+json;q=1",
        )

        response = json.loads("".join(handler._write_buffer))
        self.assertEqual({
            "error": {
                "code": 500,
                "message": "Internal Server Error",
                "request_id": handler.request_id,
            },
        }, response)
        self.assertEqual(
            "application/json; charset=UTF-8",
            handler.headers["Content-Type"],
        )

    def test_zero_quality_json_falls_back_to_html(self):
        handler, _ = exercise_uncaught_exception(
            debug=False,
            accept="application/json;q=0, text/html",
        )

        self.assertTrue("".join(handler._write_buffer).startswith("<html>"))

    def test_uncaught_exception_log_is_structured_and_redacted(self):
        handler, logging_module = exercise_uncaught_exception(
            debug=True,
            nested=True,
        )

        records = structured_log_records(logging_module)
        self.assertEqual(1, len(records))
        self.assertEqual("uncaught_exception", records[0]["event"])
        self.assertEqual(handler.request_id, records[0]["request_id"])
        self.assertEqual(
            ["RuntimeError", "ValueError"],
            records[0]["exception_types"],
        )
        serialized = json.dumps(records[0])
        for secret in (
            SENTINEL,
            CAUSE_SENTINEL,
            QUERY_SENTINEL,
            BODY_SENTINEL,
            HEADER_SENTINEL,
            "127.0.0.1",
        ):
            self.assertNotIn(secret, serialized)
        self.assertNotIn("exc_info", json.dumps(logging_module.records, default=str))

    def test_exception_context_never_reaches_custom_renderer(self):
        logging_module = CapturingLogging()
        handler_class = load_handler_class(logging_module)

        class CustomHandler(handler_class):
            def write_error(self, status_code, **kwargs):
                self.write(json.dumps(sorted(kwargs.keys())))

        handler = CustomHandler(debug=True)
        try:
            raise RuntimeError(SENTINEL)
        except RuntimeError:
            handler.send_error(500, exc_info=sys.exc_info())

        self.assertEqual("[]", "".join(handler._write_buffer))

    def test_failed_custom_renderer_discards_partial_sensitive_output(self):
        logging_module = CapturingLogging()
        handler_class = load_handler_class(logging_module)

        class BrokenHandler(handler_class):
            def write_error(self, status_code, **kwargs):
                self.write(SENTINEL)
                raise RuntimeError(CAUSE_SENTINEL)

        handler = BrokenHandler(debug=True)
        handler.send_error(500)

        response = "".join(handler._write_buffer)
        self.assertNotIn(SENTINEL, response)
        self.assertNotIn(CAUSE_SENTINEL, response)
        self.assertEqual(500, handler.status_code)
        records = structured_log_records(logging_module)
        self.assertEqual("error_renderer_failure", records[0]["event"])

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
        self.assertIn("server-side error logs use structured records", documentation)
        self.assertIn("runtime migration remains p0 before redeployment", documentation)


if __name__ == "__main__":
    unittest.main()
