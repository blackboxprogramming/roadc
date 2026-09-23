"""Invalid assignment destinations must not silently discard writes."""

import pytest

from interpreter import Interpreter
from lexer import Lexer
from parser import Parser


def parse(source):
    return Parser(Lexer(source).tokenize()).parse_program()


@pytest.mark.parametrize('target', ['1', '(1 + 2)', 'call()', '[1, 2]'])
@pytest.mark.parametrize('operator', ['=', '+=', '-=', '*=', '/='])
def test_invalid_target_is_a_located_syntax_error(target, operator):
    with pytest.raises(SyntaxError, match=r'Invalid assignment target at 1:\d+'):
        parse(f'{target} {operator} 3\n')


@pytest.mark.parametrize('value', ['1', '[]', '"text"'])
def test_non_dictionary_member_assignment_raises(value):
    with pytest.raises(TypeError, match='Member assignment requires a dictionary'):
        Interpreter().run(parse(f'let item = {value}\nitem.value = 3\n'))


def test_valid_nested_targets_and_new_dictionary_field():
    runtime = Interpreter()
    runtime.run(parse('let item = {"entries": [1]}\n'
                      'item.entries[0] = 2\nitem.extra = 3\n'
                      'item.entries[0] += item.extra\n'))
    assert runtime.global_env.get('item') == {'entries': [5], 'extra': 3}


def test_plain_assignment_retains_rhs_before_target_order(capsys):
    runtime = Interpreter()
    runtime.run(parse('let items = [0]\n'
                      'fun rhs():\n    print("rhs")\n    return 9\n'
                      'fun target():\n    print("target")\n    return items\n'
                      'target()[0] = rhs()\n'))
    assert runtime.global_env.get('items') == [9]
    assert capsys.readouterr().out == 'rhs\ntarget\n'
