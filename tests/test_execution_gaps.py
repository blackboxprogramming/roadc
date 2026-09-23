"""Parsed work must execute or fail explicitly, never disappear."""
import pytest

from interpreter import Interpreter
from lexer import Lexer
from parser import Parser


def run(source):
    runtime = Interpreter()
    runtime.run(Parser(Lexer(source).tokenize()).parse_program())
    return runtime.global_env


@pytest.mark.parametrize('operator,expected', [('+', 10), ('-', 6), ('*', 16), ('/', 4)])
@pytest.mark.parametrize('target', ['items[0]', 'record["count"]', 'record.count'])
def test_collection_compound_updates(operator, expected, target):
    env = run('let items = [8]\nlet record = {"count": 8}\n'
              f'{target} {operator}= 2\nlet result = {target}\n')
    assert env.get('result') == expected


def test_compound_target_and_rhs_evaluated_once_in_order():
    env = run('let calls = []\nlet items = [8]\n'
              'fun target():\n    calls.append("target")\n    return items\n'
              'fun index():\n    calls.append("index")\n    return 0\n'
              'fun rhs():\n    calls.append("rhs")\n    return 2\n'
              'target()[index()] += rhs()\n')
    assert env.get('items') == [10]
    assert env.get('calls') == ['target', 'index', 'rhs']


@pytest.mark.parametrize('source', ['import missing\n', 'module demo\n',
                                   'export let hidden = 1\n'])
def test_unsupported_statements_fail(source):
    with pytest.raises(RuntimeError, match='Unsupported statement'):
        run(source)


@pytest.mark.parametrize('source', ['1 = 2\n', '1 += 2\n',
                                   'let x = 1\nx.value = 2\n',
                                   'let x = 1\nx.value += 2\n'])
def test_invalid_assignment_is_not_silently_ignored(source):
    with pytest.raises((SyntaxError, TypeError, RuntimeError)):
        run(source)


def test_missing_compound_key_fails_before_rhs():
    runtime = Interpreter()
    source = ('let record = {}\nlet calls = []\n'
              'fun rhs():\n    calls.append(1)\n    return 2\n'
              'record.missing += rhs()\n')
    with pytest.raises(KeyError):
        runtime.run(Parser(Lexer(source).tokenize()).parse_program())
    assert runtime.global_env.get('calls') == []
