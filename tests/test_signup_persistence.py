#!/usr/bin/env python3
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_baseline_module():
    spec = importlib.util.spec_from_file_location(
        "nextinvite_baseline",
        str(ROOT / "scripts" / "check-baseline.py"),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeSignupModel:
    entities = {}
    calls = []

    @classmethod
    def reset(cls):
        cls.entities = {}
        cls.calls = []

    @classmethod
    def get_or_insert(cls, key_name, **values):
        cls.calls.append((key_name, values.copy()))
        if key_name not in cls.entities:
            cls.entities[key_name] = values.copy()
        return cls.entities[key_name]


class FakeSignupHandler:
    def __init__(self, body="", content_type="application/x-www-form-urlencoded"):
        self.request = type(
            "Request",
            (),
            {"body": body, "headers": {"Content-Type": content_type}},
        )()
        self.errors = []
        self.writes = []

    def get_argument(self, name, default=""):
        if name == "email":
            return "private@example.com"
        return default

    def send_error(self, status_code):
        self.errors.append(status_code)

    def write(self, value):
        self.writes.append(value)


def main():
    baseline = load_baseline_module()
    server = baseline.load_server_module()
    FakeSignupModel.reset()

    first = server.persist_signup(" User@Example.COM ", FakeSignupModel)
    second = server.persist_signup("user@example.com", FakeSignupModel)

    expected_key = server.signup_key_name("user@example.com")
    if first is not second:
        raise AssertionError("normalized retries must return the original signup entity")
    if FakeSignupModel.entities != {expected_key: {"email": "user@example.com"}}:
        raise AssertionError("signup persistence must create one normalized entity")
    if len(FakeSignupModel.calls) != 2:
        raise AssertionError("each retry must use the transactional get-or-insert boundary")

    if server.xsrf_cookie_settings({}) != {"secure": True, "httponly": True}:
        raise AssertionError("production XSRF cookies must be Secure and HttpOnly")
    if server.xsrf_cookie_settings({"SERVER_SOFTWARE": "Development/2.0"}) != {
        "secure": False,
        "httponly": True,
    }:
        raise AssertionError("legacy HTTP dev server must retain HttpOnly without Secure")

    persisted = []
    original_persist_signup = server.persist_signup
    server.persist_signup = persisted.append
    try:
        handler = FakeSignupHandler()
        server.SignUpHandler.post(handler)
    finally:
        server.persist_signup = original_persist_signup

    if persisted:
        raise AssertionError("query-only signup email must not reach persistence")
    if handler.errors != [400] or handler.writes:
        raise AssertionError("query-only signup email must fail with generic HTTP 400")

    persisted = []
    server.persist_signup = persisted.append
    try:
        handler = FakeSignupHandler("email=User%40Example.COM")
        server.SignUpHandler.post(handler)
    finally:
        server.persist_signup = original_persist_signup

    if persisted != ["user@example.com"]:
        raise AssertionError("form-encoded body email must reach persistence normalized")
    if handler.errors or handler.writes != ["ok"]:
        raise AssertionError("valid body email must keep the successful response")

    persisted = []
    server.persist_signup = persisted.append
    try:
        handler = FakeSignupHandler(
            "email=private%40example.com",
            content_type="text/plain",
        )
        server.SignUpHandler.post(handler)
    finally:
        server.persist_signup = original_persist_signup

    if persisted:
        raise AssertionError("unsupported signup content type must not persist email")
    if handler.errors != [400] or handler.writes:
        raise AssertionError("unsupported signup content type must fail with HTTP 400")

    print("signup persistence checks passed")


if __name__ == "__main__":
    main()
