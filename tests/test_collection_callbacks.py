"""Road functions should remain callable when passed to collection builtins."""

import pytest

from interpreter import Interpreter
from parser import parse


def run(source):
    runtime = Interpreter()
    runtime.run(parse(source))
    return runtime.global_env


def test_map_uses_road_functions_and_ranges():
    env = run('fun double(x):\n    return x * 2\nlet result = map(double, 1..4)\n')
    assert env.get("result") == [2, 4, 6]


def test_filter_preserves_original_values():
    env = run('fun positive(x):\n    return x > 0\nlet result = filter(positive, [-1, 0, 2, 3])\n')
    assert env.get("result") == [2, 3]


def test_callbacks_keep_separate_closures_and_defaults():
    env = run('''fun factory(seed):
    fun add(value, extra = seed):
        return value + extra
    return add
let first = factory(10)
let second = factory(20)
let a = map(first, [1, 2])
let b = map(second, [1, 2])
''')
    assert env.get("a") == [11, 12]
    assert env.get("b") == [21, 22]


def test_map_multiple_inputs_stops_at_shortest_and_supports_variadics():
    env = run('''fun combine(first, ...rest):
    return first + sum(rest)
let result = map(combine, [1, 2, 3], [10, 20], [100, 200, 300])
''')
    assert env.get("result") == [111, 222]


def test_inputs_once_then_callbacks_in_order():
    env = run('''let events = []
fun values():
    events.append("input")
    return [1, 2]
fun callback(x):
    events.append(x)
    return x
let result = map(callback, values())
''')
    assert env.get("events") == ["input", 1, 2]


@pytest.mark.parametrize("expression", [
    "map(callback)", "filter(callback)", "filter(callback, values(), values())",
    "map(7, values())", "map(wrong, values())", "filter(wrong, values())",
])
def test_invalid_calls_rejected_before_input_effects(expression):
    runtime = Interpreter()
    program = parse('''let events = []
fun values():
    events.append("input")
    return [1]
fun callback(x):
    return x
fun wrong(a, b):
    return a + b
let result = ''' + expression + '\n')
    with pytest.raises(TypeError):
        runtime.run(program)
    assert runtime.global_env.get("events") == []


def test_callback_failure_stops_processing_without_rolling_back_effects():
    runtime = Interpreter()
    with pytest.raises(ZeroDivisionError):
        runtime.run(parse('''let events = []
fun callback(x):
    events.append(x)
    return 10 / x
map(callback, [2, 0, 3])
'''))
    assert runtime.global_env.get("events") == [2, 0]


def test_member_callable_and_empty_inputs():
    env = run('''let seen = []
let result = map(seen.append, [1, 2])
fun identity(x):
    return x
let empty_map = map(identity, [])
let empty_filter = filter(identity, [])
''')
    assert env.get("seen") == [1, 2]
    assert env.get("result") == [None, None]
    assert env.get("empty_map") == env.get("empty_filter") == []


def test_callback_break_cannot_escape_callers_loop():
    with pytest.raises(RuntimeError, match="break outside a loop in this function"):
        run('fun callback(x):\n    break\nfor x in [1]:\n    map(callback, [x])\n')
