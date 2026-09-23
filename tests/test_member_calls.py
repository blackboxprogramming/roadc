"""Bound methods share builtin validation and retain their receiver."""
import pytest

from interpreter import Interpreter
from parser import parse


@pytest.mark.parametrize('member,count', [
    ('[].append', 1), ('[].pop', 0),
    ('{}.keys', 0), ('{}.values', 0), ('{}.items', 0),
    ('"text".upper', 0), ('"text".lower', 0), ('"text".strip', 0),
    ('"text".split', 1), ('"text".replace', 2),
    ('"text".startswith', 1), ('"text".endswith', 1), ('"text".contains', 1),
])
def test_invalid_member_arity_precedes_argument_effects(member, count):
    runtime = Interpreter()
    arguments = ', '.join(['mark()'] * (count + 1))
    with pytest.raises(TypeError, match='expected .* arguments'):
        runtime.run(parse('''let events = []
fun mark():
    events.append(1)
    return "x"
let method = ''' + member + '\nmethod(' + arguments + ')\n'))
    assert runtime.global_env.get('events') == []


@pytest.mark.parametrize('call', ['map([].pop, source())', 'filter("x".replace, source())'])
def test_invalid_member_callback_precedes_input_even_when_empty(call):
    runtime = Interpreter()
    with pytest.raises(TypeError, match='expected .* arguments'):
        runtime.run(parse('''let events = []
fun source():
    events.append(1)
    return []
''' + call + '\n'))
    assert runtime.global_env.get('events') == []


def test_bound_method_keeps_original_receiver_and_works_as_callback():
    runtime = Interpreter()
    runtime.run(parse('''let original = []
let items = original
let add = items.append
items = []
let results = map(add, [3, 1, 2])
let kept = filter("hello".contains, ["h", "x", "lo"])
let replaced = map("aba".replace, ["a", "b"], ["x", "y"])
let popped = original.pop()
'''))
    env = runtime.global_env
    assert env.get('original') == [3, 1]
    assert env.get('items') == []
    assert env.get('results') == [None, None, None]
    assert env.get('kept') == ['h', 'lo']
    assert env.get('replaced') == ['xbx', 'aya']
    assert env.get('popped') == 2


@pytest.mark.parametrize('expression,expected', [
    ('" a b ".split()', ['', 'a', 'b', '']),
    ('"a,b".split(",")', ['a', 'b']),
    ('" Ab ".strip().upper()', 'AB'),
    ('"Ab".lower()', 'ab'),
    ('"abc".startswith("a")', True),
    ('"abc".endswith("c")', True),
    ('{"a": 1}.keys()', ['a']),
    ('{"a": 1}.values()', [1]),
    ('{"a": 1}.items()', [('a', 1)]),
    ('[1, 2].length', 2),
    ('"abc".length', 3),
])
def test_existing_member_results(expression, expected):
    runtime = Interpreter()
    runtime.run(parse('let result = ' + expression + '\n'))
    assert runtime.global_env.get('result') == expected
