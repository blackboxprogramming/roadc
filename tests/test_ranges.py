"""Range syntax must work through both the parser and interpreter."""

import pytest

from ast_nodes import BinaryOp, RangeExpression
from interpreter import Interpreter
from lexer import Lexer
from parser import Parser


def parse(source):
    return Parser(Lexer(source).tokenize()).parse_program()


def run(source):
    interpreter = Interpreter()
    interpreter.run(parse(source))
    return interpreter.global_env


@pytest.mark.parametrize("expression, expected", [
    ("0..4", [0, 1, 2, 3]),
    ("0 .. 4", [0, 1, 2, 3]),
    ("-2..2", [-2, -1, 0, 1]),
    ("-4..-1", [-4, -3, -2]),
    ("3..3", []),
    ("4..2", []),
    ("1 + 1..2 * 3", [2, 3, 4, 5]),
    ("(1 + 1)..(2 + 3)", [2, 3, 4]),
])
def test_exclusive_bounds(expression, expected):
    result = run("let result = " + expression + "\n").get("result")
    assert isinstance(result, range)
    assert list(result) == expected


def test_quickstart_loop(capsys):
    run("for i in 0..3:\n    print(i)\n")
    assert capsys.readouterr().out == "0\n1\n2\n"


def test_variable_bounds():
    env = run("let start = -1\nlet stop = 2\nlet result = start..stop\n")
    assert list(env.get("result")) == [-1, 0, 1]


def test_bounds_evaluated_once_in_order(capsys):
    env = run('fun bound(value):\n    print(value)\n    return value\n'
              'let result = bound(1)..bound(3)\n')
    assert capsys.readouterr().out == "1\n3\n"
    assert list(env.get("result")) == [1, 2]


def test_function_argument_and_index():
    env = run("fun first(items):\n    return items[0]\n"
              "let result = first(2..5)\nlet second = (2..5)[1]\n")
    assert env.get("result") == 2
    assert env.get("second") == 3


def test_range_is_lazy():
    result = run("let result = 0..1000000000000\n").get("result")
    assert isinstance(result, range)
    assert result[-1] == 999999999999


def test_precedence_and_operator_location():
    expression = parse("let result = 0..1 + 2 == 0..3\n").statements[0].initializer
    assert isinstance(expression, BinaryOp)
    assert expression.operator == "=="
    assert isinstance(expression.left, RangeExpression)
    assert isinstance(expression.left.end, BinaryOp)
    assert (expression.left.line, expression.left.column) == (1, 15)


@pytest.mark.parametrize("expression", ["0..", "..3", "0..2..4", "0...3"])
def test_invalid_range_syntax(expression):
    with pytest.raises(SyntaxError):
        parse("let result = " + expression + "\n")


@pytest.mark.parametrize("expression", ["1.5..3", "0..3.5", "false..3", '0.."3"'])
def test_noninteger_bounds_report_operator_location(expression):
    with pytest.raises(TypeError, match=r"Range bounds must be integers at 1:\d+"):
        run("let result = " + expression + "\n")
