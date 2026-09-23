"""Membership expressions integrate collections, chains and guards."""

import pytest

from interpreter import Interpreter
from parser import parse


def run(source):
    runtime = Interpreter()
    runtime.run(parse(source))
    return runtime.global_env


@pytest.mark.parametrize("expression,expected", [
    ("2 in [1, 2]", True), ("3 in [1, 2]", False),
    ("3 not in [1, 2]", True), ("2 not in [1, 2]", False),
    ('"read" in {"read", "write"}', True),
    ('"name" in {"name": "Lucidia"}', True),
    ('"Lucidia" in {"name": "Lucidia"}', False),
    ('"road" in "blackroad"', True), ("2 in (1, 2)", True),
    ("2 in 0..3", True), ("not 2 in [1, 2]", False),
    ("1 < 2 in [2, 3]", True), ("3 < 2 in missing", False),
    ("4 | 2 in [6]", True),
])
def test_membership(expression, expected):
    assert run("let result = " + expression + "\n").get("result") is expected


def test_operands_are_evaluated_once_in_order():
    env = run('''let events = []
fun needle():
    events.append("needle")
    return 2
fun haystack():
    events.append("haystack")
    return [1, 2]
let result = needle() in haystack()
''')
    assert env.get("result") is True
    assert env.get("events") == ["needle", "haystack"]


def test_membership_guard_with_record_fields():
    env = run('''type Device:
    permissions: set[string]
let device = Device{permissions: {"read"}}
let allowed = "write" in device.permissions and missing()
let observed = "read" in device.permissions
''')
    assert env.get("allowed") is False
    assert env.get("observed") is True


def test_membership_does_not_change_for_loops():
    env = run('''let matches = []
for item in [1, 2, 3]:
    if item not in [2]:
        matches.append(item)
''')
    assert env.get("matches") == [1, 3]


def test_noncontainer_reports_type_error():
    with pytest.raises(TypeError):
        run("let result = 1 in 3\n")
