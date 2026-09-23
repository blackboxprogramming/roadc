"""Operators advertised by the runtime must be reachable through the parser."""

import pytest

from interpreter import Interpreter
from parser import parse


def run(source):
    runtime = Interpreter()
    runtime.run(parse(source))
    return runtime.global_env


@pytest.mark.parametrize("expression,expected", [
    ("6 & 3", 2), ("4 | 1", 5), ("7 ^ 3", 4), ("~0", -1),
    ("~6 & 7", 1), ("1 | 2 & 4", 1), ("7 ^ 3 & 1", 6),
    ("1 | 3 ^ 1", 3), ("1 + 2 & 2", 2), ("(1 | 2) & 2", 2),
    ("6 & 2 == 2", True), ("not 4 & 1", True),
    ("{1, 2} & {2, 3}", {2}), ("{1} | {2}", {1, 2}),
    ("{1, 2} ^ {2, 3}", {1, 3}),
])
def test_bitwise_and_set_operators(expression, expected):
    assert run("let result = " + expression + "\n").get("result") == expected


def test_range_bounds_accept_bitwise_expressions():
    env = run("let values = 1 | 2..4 | 1\n")
    assert list(env.get("values")) == [3, 4]


def test_operands_run_once_left_to_right():
    env = run('''let events = []
fun mark(value):
    events.append(value)
    return value
let result = mark(4) | mark(2) & mark(3)
''')
    assert env.get("result") == 6
    assert env.get("events") == [4, 2, 3]


def test_logical_guards_still_skip_bitwise_operands():
    env = run("let a = false and missing & 3\nlet b = true or ~missing\n")
    assert env.get("a") is False
    assert env.get("b") is True


@pytest.mark.parametrize("expression", ["1 &", "| 1", "1 ^ ^ 2", "~"])
def test_incomplete_operators_are_syntax_errors(expression):
    with pytest.raises(SyntaxError):
        parse("let result = " + expression + "\n")


def test_invalid_values_raise_type_error():
    with pytest.raises(TypeError):
        run('let result = "text" & 3\n')
