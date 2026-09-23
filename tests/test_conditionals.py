"""Branch selection and indentation regressions for the Python interpreter."""

import pytest

from interpreter import Interpreter
from lexer import Lexer
from parser import Parser


def run(source):
    runtime = Interpreter()
    runtime.run(Parser(Lexer(source).tokenize()).parse_program())
    return runtime.global_env


@pytest.mark.parametrize('value, expected', [(0, 10), (1, 20), (2, 30), (3, 40)])
def test_if_elif_else_selects_one_branch(value, expected):
    env = run(f'let value = {value}\nlet result = 0\n'
              'if value == 0:\n    result = 10\n'
              'elif value == 1:\n    result = 20\n'
              'elif value == 2:\n    result = 30\n'
              'else:\n    result = 40\n'
              'let after = result + 1\n')
    assert env.get('result') == expected
    assert env.get('after') == expected + 1


@pytest.mark.parametrize('outer, inner, expected', [
    ('true', 'true', 1), ('true', 'false', 2), ('false', 'true', 3),
])
def test_nested_else_belongs_to_its_indentation(outer, inner, expected):
    env = run('let result = 0\n'
              f'if {outer}:\n    if {inner}:\n        result = 1\n'
              '    else:\n        result = 2\n'
              'else:\n    result = 3\n'
              'let after = 99\n')
    assert env.get('result') == expected
    assert env.get('after') == 99


def test_selected_branch_skips_later_condition_and_body(capsys):
    env = run('let result = 0\nif true:\n    result = 1\n'
              'elif missing:\n    print("elif")\n'
              'else:\n    print("else")\n')
    assert env.get('result') == 1
    assert capsys.readouterr().out == ''


def test_logical_guards_in_function_conditions():
    env = run('fun choose(value):\n'
              '    if value and missing:\n        return 1\n'
              '    elif true or missing:\n        return 2\n'
              '    else:\n        return 3\n'
              'let result = choose(false)\n')
    assert env.get('result') == 2
