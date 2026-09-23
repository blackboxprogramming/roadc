"""Regression coverage for user-defined function argument binding."""
import pytest

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter


def run(source):
    runtime = Interpreter()
    runtime.run(Parser(Lexer(source).tokenize()).parse_program())
    return runtime.global_env


@pytest.mark.parametrize('call', ['pick()', 'pick(1, print("argument"))'])
def test_wrong_arity_rejected_before_effects(call, capsys):
    with pytest.raises(TypeError, match='pick'):
        run('let x = 99\nfun pick(x):\n    print("body")\n    return x\nlet result = ' + call + '\n')
    assert capsys.readouterr().out == ''


def test_defaults_use_definition_scope_and_earlier_parameters():
    env = run('let seed = 4\nfun pick(a, b = a + seed):\n    return b\nfun caller(seed):\n    return pick(3)\nlet result = caller(100)\n')
    assert env.get('result') == 7


def test_supplied_argument_skips_default():
    assert run('fun pick(x = missing):\n    return x\nlet result = pick(8)\n').get('result') == 8


def test_mutable_literal_defaults_are_fresh():
    env = run('fun pick(xs = []):\n    xs.append(1)\n    return len(xs)\nlet first = pick()\nlet second = pick()\n')
    assert (env.get('first'), env.get('second')) == (1, 1)


@pytest.mark.parametrize('call, expected', [('pick(1)', []), ('pick(1, 2, 3)', [2, 3])])
def test_variadic_tail(call, expected):
    assert run('fun pick(first, ...rest):\n    return rest\nlet result = ' + call + '\n').get('result') == expected


@pytest.mark.parametrize('params', ['x, x', '...xs, y', '...xs = []', 'x = 1, y'])
def test_invalid_signature_rejected_before_effects(params, capsys):
    with pytest.raises(TypeError, match='pick'):
        run('fun pick(' + params + '):\n    print("body")\npick(print("argument"))\n')
    assert capsys.readouterr().out == ''


def test_arguments_evaluated_once_left_to_right(capsys):
    run('fun mark(x):\n    print(x)\n    return x\nfun pick(a, b):\n    return a + b\nlet result = pick(mark(1), mark(2))\n')
    assert capsys.readouterr().out == '1\n2\n'


def test_default_failure_propagates():
    with pytest.raises(NameError, match='missing'):
        run('fun pick(x = missing):\n    return x\npick()\n')


def test_zero_parameters_and_recursion():
    env = run('fun zero():\n    return 0\nfun count(n):\n    if n == 0:\n        return zero()\n    return 1 + count(n - 1)\nlet result = count(4)\n')
    assert env.get('result') == 4
