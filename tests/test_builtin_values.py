"""Builtin values follow the same call rules through aliases and callbacks."""

import pytest
from pathlib import Path

from interpreter import Interpreter
from parser import parse


def run(source):
    runtime = Interpreter()
    runtime.run(parse(source))
    return runtime.global_env


def test_builtin_callbacks_convert_and_filter_values():
    env = run('let text = map(str, [1, 2])\nlet kept = filter(bool, [0, 2, "", "ok"])\n')
    assert env.get("text") == ["1", "2"]
    assert env.get("kept") == [2, "ok"]


@pytest.mark.parametrize("name,value,expected", [
    ("int", '"12"', 12), ("float", '"1.5"', 1.5), ("bool", "0", False),
    ("list", "1..3", [1, 2]), ("dict", '[("a", 1)]', {"a": 1}),
    ("set", "[1, 1]", {1}),
])
def test_type_keyword_values_and_aliases(name, value, expected):
    env = run(f'let convert = {name}\nlet result = convert({value})\n')
    assert env.get("result") == expected


def test_builtins_pass_through_road_functions_and_containers():
    env = run('''fun apply(operation, value):
    return operation(value)
fun choose():
    return abs
let operations = [str, choose()]
let text = apply(operations[0], 12)
let magnitude = operations[1](-7)
''')
    assert env.get("text") == "12"
    assert env.get("magnitude") == 7


def test_collection_aliases_and_nested_callbacks():
    env = run('''let transform = map
let keep = filter
let lengths = transform(len, [[1], [2, 3]])
let nonempty = keep(len, [[], [1]])
let nested = map(map, [str, abs], [[1, 2], [-3, 4]])
''')
    assert env.get("lengths") == [1, 2]
    assert env.get("nonempty") == [[1]]
    assert env.get("nested") == [["1", "2"], [3, 4]]


@pytest.mark.parametrize("expression", [
    "convert(mark(), mark())", "transform(len, mark(), mark())",
    "transform(isinstance, mark())", "keep(isinstance, mark())",
    "transform(len)", "transform(len, [], [])",
])
def test_alias_and_callback_arity_precede_argument_effects(expression):
    runtime = Interpreter()
    with pytest.raises(TypeError, match="expected"):
        runtime.run(parse('''let events = []
let convert = str
let transform = map
let keep = filter
fun mark():
    events.append("called")
    return [1]
let result = ''' + expression + '\n'))
    assert runtime.global_env.get("events") == []


def test_lexical_binding_consistent_in_direct_and_indirect_calls():
    env = run('''let original = len
fun len(value):
    return 99
let alias = len
let direct = len([1, 2])
let indirect = alias([1, 2])
let preserved = original([1, 2])
fun apply(map):
    return map(-4)
let parameter = apply(abs)
''')
    assert env.get("direct") == env.get("indirect") == 99
    assert env.get("preserved") == 2
    assert env.get("parameter") == 4


def test_runtime_builtin_bindings_do_not_leak_between_interpreters():
    run('let len = 7\n')
    assert run('let result = len([1])\n').get("result") == 1


def test_builtin_callback_error_stops_after_prior_effects():
    runtime = Interpreter()
    with pytest.raises(ValueError):
        runtime.run(parse('''let seen = []
fun convert(value):
    seen.append(value)
    return int(value)
map(convert, ["1", "bad", "3"])
'''))
    assert runtime.global_env.get("seen") == ["1", "bad"]


def test_builtin_defaults_and_input_evaluation_order():
    env = run('''let events = []
fun values(label, value):
    events.append(label)
    return value
fun convert(value, operation = int):
    return operation(value)
let alias = map
let result = alias(round, values("first", [1.234, 5.678]), values("second", [1, 2]))
let converted = convert("12")
''')
    assert env.get("events") == ["first", "second"]
    assert env.get("result") == [1.2, 5.68]
    assert env.get("converted") == 12


def test_noncallable_shadow_does_not_fall_back_to_builtin_or_run_arguments():
    runtime = Interpreter()
    with pytest.raises(RuntimeError, match="not callable"):
        runtime.run(parse('''let events = []
let len = 3
fun mark():
    events.append("called")
    return []
len(mark())
'''))
    assert runtime.global_env.get("events") == []


def test_documented_example_runs(capsys):
    source = Path(__file__).resolve().parents[1] / "examples" / "builtin_callbacks.road"
    run(source.read_text(encoding="utf-8"))
    assert capsys.readouterr().out == "['3', '7']\n10\n"
