"""Adjacent collection elements require explicit comma separators."""

import pytest

from interpreter import Interpreter
from lexer import Lexer
from parser import Parser


def parse(expression):
    return Parser(Lexer('let result = ' + expression + '\n').tokenize()).parse_program()


@pytest.mark.parametrize('expression', [
    '[1 2]', '[true false]', '[[1], 2 3]', '[f() g()]',
    'vec2(1 2)', 'vec3(1, 2 3)', 'vec4(1 2, 3, 4)',
])
def test_missing_comma_is_rejected(expression):
    with pytest.raises(SyntaxError):
        parse(expression)


@pytest.mark.parametrize('expression, expected', [
    ('[]', []), ('[1]', [1]), ('[1, 2,]', [1, 2]),
    ('[[1], [2]]', [[1], [2]]), ('[1 + 2, -3]', [3, -3]),
    ('[[8, 9][1]]', [9]),
    ('vec2(1, 2)', (1, 2)), ('vec3(1, 2, 3,)', (1, 2, 3)),
    ('vec4(1, 2, 3, 4)', (1, 2, 3, 4)),
])
def test_valid_elements_and_trailing_commas(expression, expected):
    runtime = Interpreter()
    runtime.run(parse(expression))
    assert runtime.global_env.get('result') == expected
