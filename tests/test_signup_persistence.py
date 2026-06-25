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

    print("signup persistence checks passed")


if __name__ == "__main__":
    main()
