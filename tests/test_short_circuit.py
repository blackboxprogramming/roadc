"""Logical guards must not execute an unnecessary right-hand operand."""

import pytest

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter


def evaluate(expression):
    runtime = Interpreter()
    runtime.run(Parser(Lexer(f"let result = {expression}\n").tokenize()).parse_program())
    return runtime.global_env.get("result")


@pytest.mark.parametrize("expression, expected", [
    ("false and missing", False),
    ("true or missing", True),
    ("false and (1 / 0)", False),
    ("true or (1 / 0)", True),
    ('0 and 9', 0),
    ('7 or 9', 7),
    ('7 and 9', 9),
    ('0 or 9', 9),
])
def test_guard_and_operand_values(expression, expected):
    assert evaluate(expression) == expected


@pytest.mark.parametrize("expression", ["true and missing", "false or missing"])
def test_required_operand_still_raises(expression):
    with pytest.raises(NameError, match="missing"):
        evaluate(expression)


@pytest.mark.parametrize("expression, expected", [
    ('false and print("effect")', ""),
    ('true or print("effect")', ""),
    ('true and print("effect")', "effect\n"),
    ('false or print("effect")', "effect\n"),
])
def test_side_effect_runs_only_when_needed(expression, expected, capsys):
    evaluate(expression)
    assert capsys.readouterr().out == expected
