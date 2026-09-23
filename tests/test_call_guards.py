"""Interaction coverage for logical guards and function argument binding."""

import pytest

from interpreter import Interpreter
from lexer import Lexer
from parser import Parser


def run(source):
    runtime = Interpreter()
    runtime.run(Parser(Lexer(source).tokenize()).parse_program())
    return runtime.global_env


@pytest.mark.parametrize('expression, expected', [
    ('false and pick()', False),
    ('true or pick()', True),
])
def test_skipped_call_does_not_validate_arity(expression, expected):
    env = run('fun pick(x):\n    return x\nlet result = ' + expression + '\n')
    assert env.get('result') is expected


@pytest.mark.parametrize('expression', ['true and pick()', 'false or pick()'])
def test_required_call_validates_arity(expression):
    with pytest.raises(TypeError, match='pick'):
        run('fun pick(x):\n    return x\nlet result = ' + expression + '\n')


def test_defaults_short_circuit_in_parameter_scope(capsys):
    env = run('fun pick(a, b = a or print("default")):\n    return b\n'
              'let first = pick(7)\nlet second = pick(0)\n')
    assert env.get('first') == 7
    assert env.get('second') is None
    assert capsys.readouterr().out == 'default\n'


def test_variadic_arguments_preserve_guard_values_and_effect_order(capsys):
    env = run('fun mark(x):\n    print(x)\n    return x\n'
              'fun collect(...xs):\n    return xs\n'
              'let result = collect(false and missing, true or missing, '
              'true and mark(1), false or mark(2))\n')
    assert env.get('result') == [False, True, 1, 2]
    assert capsys.readouterr().out == '1\n2\n'
