"""Compound updates must evaluate and write collection targets."""

import pytest

from interpreter import Interpreter
from lexer import Lexer
from parser import Parser


def run(source):
    runtime = Interpreter()
    runtime.run(Parser(Lexer(source).tokenize()).parse_program())
    return runtime.global_env


@pytest.mark.parametrize('op, expected', [('+=', 10), ('-=', 6), ('*=', 16), ('/=', 4)])
@pytest.mark.parametrize('setup, target', [
    ('let item = [8]', 'item[0]'),
    ('let item = {"value": 8}', 'item["value"]'),
    ('let item = {"value": 8}', 'item.value'),
])
def test_collection_update(setup, target, op, expected):
    env = run(f'{setup}\n{target} {op} 2\nlet result = {target}\n')
    assert env.get('result') == expected


def test_target_then_index_then_rhs_evaluated_once(capsys):
    env = run('let values = [8]\n'
              'fun target():\n    print("target")\n    return values\n'
              'fun index():\n    print("index")\n    return 0\n'
              'fun rhs():\n    print("rhs")\n    values[0] = 100\n    return 2\n'
              'target()[index()] += rhs()\n')
    assert env.get('values') == [10]
    assert capsys.readouterr().out == 'target\nindex\nrhs\n'


@pytest.mark.parametrize('source, error', [
    ('let x = []\nx[0] += print("rhs")\n', IndexError),
    ('let x = {}\nx.absent += print("rhs")\n', KeyError),
    ('let x = 1\nx.value += print("rhs")\n', TypeError),
    ('1 += print("rhs")\n', SyntaxError),
])
def test_invalid_target_fails_before_rhs(source, error, capsys):
    with pytest.raises(error):
        run(source)
    assert capsys.readouterr().out == ''
