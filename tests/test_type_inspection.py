"""Road source can inspect local values through builtin constructor values."""

import pytest

from interpreter import Interpreter
from parser import parse


def run(source):
    runtime = Interpreter()
    runtime.run(parse(source))
    return runtime.global_env


@pytest.mark.parametrize("value,name", [
    ("1", "int"), ("1.5", "float"), ("true", "bool"), ('"text"', "str"),
    ("[1]", "list"), ('{"x": 1}', "dict"), ("{1, 2}", "set"),
    ("(1, 2)", "tuple"), ("0..3", "range"),
])
def test_type_reports_existing_runtime_value_names(value, name):
    assert run(f'let result = type({value})\n').get("result") == name


def test_type_value_alias_callback_and_declaration_coexist():
    env = run('''type Task:
    count: int = 3
let task = Task{}
let inspect_value = type
let record_kind = inspect_value(task)
let kinds = map(type, [1, "text", true])
type(1)
''')
    assert env.get("record_kind") == "dict"
    assert env.get("kinds") == ["int", "str", "bool"]


@pytest.mark.parametrize("expression,expected", [
    ("isinstance(1, int)", True), ("isinstance(1.5, float)", True),
    ("isinstance(true, bool)", True), ("isinstance(true, int)", True),
    ("isinstance(1, bool)", False), ('isinstance("1", str)', True),
    ("isinstance([], list)", True), ("isinstance({}, dict)", True),
    ("isinstance({1}, set)", True), ("isinstance(1, float)", False),
    ("isinstance(1, (str, (float, int)))", True),
    ("isinstance(1, ())", False),
])
def test_basic_constructor_type_checks(expression, expected):
    assert run('let result = ' + expression + '\n').get("result") is expected


def test_constructor_and_predicate_aliases_and_callbacks():
    env = run('''let number_type = int
let check_value = isinstance
let direct = check_value(7, number_type)
let flags = map(check_value, [1, "x", true], [number_type, str, bool])
fun numeric(value):
    return check_value(value, (int, float))
let kept = filter(numeric, [1, "x", 2.5])
''')
    assert env.get("direct") is True
    assert env.get("flags") == [True, True, True]
    assert env.get("kept") == [1, 2.5]


@pytest.mark.parametrize("descriptor", ['"int"', "1", "len", "[int]", "(int, 7)", "range"])
def test_invalid_descriptors_fail_even_after_a_matching_tuple_entry(descriptor):
    with pytest.raises(TypeError, match="isinstance: expected a builtin type"):
        run('let result = isinstance(1, ' + descriptor + ')\n')


def test_record_declarations_are_not_nominal_type_descriptors():
    with pytest.raises(TypeError, match="isinstance: expected a builtin type"):
        run('type Task:\n    count: int = 1\nlet task = Task{}\nisinstance(task, Task)\n')


def test_shadowed_constructor_name_is_not_mistaken_for_a_type():
    with pytest.raises(TypeError, match="isinstance: expected a builtin type"):
        run('let str = 9\nisinstance("text", str)\n')


def test_inspection_arity_is_checked_before_argument_effects():
    runtime = Interpreter()
    with pytest.raises(TypeError, match="type: expected"):
        runtime.run(parse('''let seen = []
fun mark():
    seen.append(1)
    return 1
type(mark(), mark())
'''))
    assert runtime.global_env.get("seen") == []


def test_saved_constructor_alias_survives_shadowing():
    env = run('let text_type = str\nlet str = 9\nlet result = isinstance("text", text_type)\n')
    assert env.get("result") is True


def test_host_supplied_type_objects_remain_supported():
    runtime = Interpreter()
    runtime.global_env.set("HostType", str)
    runtime.run(parse('let result = isinstance("text", HostType)\n'))
    assert runtime.global_env.get("result") is True
