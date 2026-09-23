"""Vector constructors must match their declared dimension."""

import pytest

from interpreter import Interpreter
from lexer import Lexer
from parser import Parser


def run(source):
    runtime = Interpreter()
    runtime.run(Parser(Lexer(source).tokenize()).parse_program())
    return runtime.global_env


@pytest.mark.parametrize('dimension', [2, 3, 4])
@pytest.mark.parametrize('offset', [-1, 1])
def test_wrong_component_count_fails_before_effects(dimension, offset, capsys):
    components = ', '.join('print("component")' for _ in range(dimension + offset))
    with pytest.raises(TypeError, match=f'vec{dimension}: expected {dimension} components'):
        run(f'let result = vec{dimension}({components})\n')
    assert capsys.readouterr().out == ''


@pytest.mark.parametrize('dimension', [2, 3, 4])
def test_valid_components_evaluated_once_in_order(dimension, capsys):
    components = ', '.join(f'mark({i})' for i in range(dimension))
    env = run('fun mark(x):\n    print(x)\n    return x\n'
              f'let result = vec{dimension}({components})\n')
    assert env.get('result') == tuple(range(dimension))
    assert capsys.readouterr().out == ''.join(f'{i}\n' for i in range(dimension))


def test_guard_skips_invalid_vector_constructor():
    assert run('let result = false and vec3()\n').get('result') is False


def test_valid_shape_still_propagates_component_errors():
    with pytest.raises(NameError, match='missing'):
        run('let result = vec2(1, missing)\n')
