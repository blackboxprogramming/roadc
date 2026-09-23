"""Invalid top-level control flow must report language errors."""

import pytest

from interpreter import Interpreter
from lexer import Lexer
from parser import Parser


def program(source):
    return Parser(Lexer(source).tokenize()).parse_program()


@pytest.mark.parametrize('statement, message', [
    ('return 3', 'return outside a function'),
    ('break', 'break outside a loop'),
    ('continue', 'continue outside a loop'),
])
@pytest.mark.parametrize('nested', [False, True])
def test_invalid_top_level_control(statement, message, nested):
    source = f'if true:\n    {statement}\n' if nested else statement + '\n'
    runtime = Interpreter()
    with pytest.raises(RuntimeError, match=message):
        runtime.run(program(source))
    runtime.run(program('let recovered = 7\n'))
    assert runtime.global_env.get('recovered') == 7


def test_top_level_return_inside_loop_is_still_invalid():
    with pytest.raises(RuntimeError, match='return outside a function'):
        Interpreter().run(program('for i in range(2):\n    return i\n'))


def test_valid_top_level_loop_control_and_function_return():
    runtime = Interpreter()
    runtime.run(program('let total = 0\nfor i in range(5):\n'
                        '    if i == 1:\n        continue\n'
                        '    if i == 3:\n        break\n'
                        '    total += i\n'
                        'fun get():\n    return total\nlet result = get()\n'))
    assert runtime.global_env.get('result') == 2
