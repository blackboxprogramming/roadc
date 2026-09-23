"""Exponentiation binds before a leading sign, but accepts signed exponents."""

import pytest

from interpreter import Interpreter
from parser import parse


@pytest.mark.parametrize("expression,expected", [
    ("-2 ** 2", -4), ("(-2) ** 2", 4), ("2 ** -2", 0.25),
    ("-2 ** -2", -0.25), ("2 ** 3 ** 2", 512), ("(2 ** 3) ** 2", 64),
    ("~2 ** 3", -9), ("2 ** ~1", 0.25), ("--2 ** 2", 4),
    ("3 * -2 ** 2", -12), ("+2 ** 3", 8), ("-2 ** 2 < 0", True),
])
def test_power_and_unary_precedence(expression, expected):
    runtime = Interpreter()
    runtime.run(parse("let result = " + expression + "\n"))
    assert runtime.global_env.get("result") == expected


def test_calls_remain_single_evaluation_left_to_right():
    runtime = Interpreter()
    runtime.run(parse('''let events = []
fun mark(x):
    events.append(x)
    return x
let result = -mark(2) ** mark(3) ** mark(2)
'''))
    assert runtime.global_env.get("result") == -512
    assert runtime.global_env.get("events") == [2, 3, 2]


@pytest.mark.parametrize("expression", ["2 **", "** 2", "2 ** -", "~"])
def test_incomplete_power_or_unary_expression_fails(expression):
    with pytest.raises(SyntaxError):
        parse("let result = " + expression + "\n")
