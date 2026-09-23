"""Chained comparisons share middle values and stop on the first false pair."""

import pytest

from interpreter import Interpreter
from parser import parse


def run(source):
    runtime = Interpreter()
    runtime.run(parse(source))
    return runtime.global_env


@pytest.mark.parametrize("expression,expected", [
    ("3 < 2 < 1", False), ("1 < 2 < 3", True),
    ("1 == 1 == 1", True), ("1 == 2 == 0", False),
    ("3 > 2 >= 2", True), ("1 <= 2 != 3", True),
    ("3 > 2 > 4", False), ('"a" < "b" < "c"', True),
    ("(3 < 2) < 1", True), ("0 < (1 | 2) < 4", True),
    ("not 1 < 2 < 3", False),
])
def test_comparison_results(expression, expected):
    assert run("let result = " + expression + "\n").get("result") is expected


def test_middle_values_are_evaluated_once_in_order():
    env = run('''let events = []
fun mark(x):
    events.append(x)
    return x
let result = mark(1) < mark(2) <= mark(3) != mark(4)
''')
    assert env.get("result") is True
    assert env.get("events") == [1, 2, 3, 4]


def test_false_pair_skips_remaining_calls_and_errors():
    env = run('''let events = []
fun mark(x):
    events.append(x)
    return x
let result = mark(3) < mark(2) < missing()
''')
    assert env.get("result") is False
    assert env.get("events") == [3, 2]


def test_reached_comparison_errors_propagate():
    with pytest.raises(TypeError):
        run('let result = 1 < 2 < "three"\n')


def test_logical_guard_skips_entire_chain():
    env = run("let a = false and missing < 2 < 3\nlet b = true or missing < 2 < 3\n")
    assert env.get("a") is False
    assert env.get("b") is True
