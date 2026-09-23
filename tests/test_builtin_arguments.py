"""Builtin adapters must not silently discard arguments or their effects."""

import pytest

from interpreter import Interpreter
from parser import parse


@pytest.mark.parametrize("expression,name", [
    ("len([1], mark())", "len"),
    ("abs(1, mark())", "abs"),
    ("int(1, mark())", "int"),
    ("sum([1], mark())", "sum"),
    ("sorted([1], mark())", "sorted"),
    ("enumerate([1], mark())", "enumerate"),
    ("list([1], mark())", "list"),
    ("dict({}, mark())", "dict"),
    ("set([1], mark())", "set"),
    ("round(1, 0, mark())", "round"),
    ("input(\"prompt\", mark())", "input"),
    ("range(1, 3, 1, mark())", "range"),
    ("len()", "len"),
    ("min()", "min"),
    ("max()", "max"),
    ("range()", "range"),
])
def test_invalid_builtin_arity_precedes_argument_effects(expression, name):
    runtime = Interpreter()
    with pytest.raises(TypeError, match=name + ": expected"):
        runtime.run(parse('''let events = []
fun mark():
    events.append("called")
    return 1
let result = ''' + expression + '\n'))
    assert runtime.global_env.get("events") == []


def test_builtin_arguments_evaluate_once_in_order():
    runtime = Interpreter()
    runtime.run(parse('''let events = []
fun mark(x):
    events.append(x)
    return x
let result = min(mark(3), mark(1), mark(2))
'''))
    assert runtime.global_env.get("result") == 1
    assert runtime.global_env.get("events") == [3, 1, 2]


def test_supported_empty_optional_and_variadic_calls():
    runtime = Interpreter()
    runtime.run(parse('''let empty_list = list()
let empty_dict = dict()
let empty_set = set()
let empty_zip = zip()
let rounded = round(1.234, 2)
let low = min([3, 1, 2])
let high = max(3, 1, 2)
let stepped = list(range(1, 6, 2))
'''))
    env = runtime.global_env
    assert env.get("empty_list") == env.get("empty_zip") == []
    assert env.get("empty_dict") == {}
    assert env.get("empty_set") == set()
    assert env.get("rounded") == 1.23
    assert env.get("low") == 1
    assert env.get("high") == 3
    assert env.get("stepped") == [1, 3, 5]


def test_short_circuit_skips_builtin_validation():
    runtime = Interpreter()
    runtime.run(parse('let a = false and len()\nlet b = true or range()\n'))
    assert runtime.global_env.get("a") is False
    assert runtime.global_env.get("b") is True


@pytest.mark.parametrize("expression,expected", [
    ('int("12")', 12), ('float("1.5")', 1.5), ('bool(0)', False),
    ('list(1..4)', [1, 2, 3]), ('dict([("a", 1)])', {"a": 1}),
    ('set([1, 1, 2])', {1, 2}),
])
def test_type_keyword_constructors_are_reachable(expression, expected):
    runtime = Interpreter()
    runtime.run(parse('let result = ' + expression + '\n'))
    assert runtime.global_env.get("result") == expected


def test_constructor_calls_preserve_type_annotations():
    runtime = Interpreter()
    runtime.run(parse('''type Record:
    number: int = int("3")
    values: list[int] = list(0..2)
fun convert(value: float) -> int:
    return int(value)
let record: Record = Record{}
let converted: int = convert(float("4.9"))
'''))
    assert runtime.global_env.get("record") == {"number": 3, "values": [0, 1]}
    assert runtime.global_env.get("converted") == 4
