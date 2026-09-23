"""A called function cannot break or continue its caller's loop."""

import pytest

from interpreter import Interpreter
from lexer import Lexer
from parser import Parser


def run(source):
    runtime = Interpreter()
    runtime.run(Parser(Lexer(source).tokenize()).parse_program())
    return runtime.global_env


@pytest.mark.parametrize('control', ['break', 'continue'])
@pytest.mark.parametrize('loop', [
    'for i in range(2):\n    bad()\n',
    'let i = 0\nwhile i < 2:\n    i = i + 1\n    bad()\n',
])
def test_function_cannot_control_caller_loop(control, loop):
    with pytest.raises(RuntimeError, match=f'bad: {control} outside a loop'):
        run(f'fun bad():\n    {control}\n' + loop)


@pytest.mark.parametrize('control', ['break', 'continue'])
def test_nested_function_cannot_control_enclosing_function_loop(control):
    with pytest.raises(RuntimeError, match=f'inner: {control} outside a loop'):
        run('fun outer():\n'
            f'    fun inner():\n        {control}\n'
            '    for i in range(2):\n        inner()\n'
            'outer()\n')


@pytest.mark.parametrize('loop', [
    'for i in range(5):\n',
    'let i = -1\nwhile i < 4:\n    i = i + 1\n',
])
def test_function_local_loop_control_and_return_remain_valid(loop):
    body = ('let total = 0\n' + loop +
            '    if i == 1:\n        continue\n'
            '    if i == 3:\n        break\n'
            '    total = total + i\n'
            'return total\n')
    env = run('fun count():\n' + ''.join('    ' + line + '\n' for line in body.splitlines()) +
              'let result = count()\n')
    assert env.get('result') == 2
