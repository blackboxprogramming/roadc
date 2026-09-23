"""Trailing commas should work consistently without accepting missing values."""

import pytest

from interpreter import Interpreter
from parser import parse


def run(source):
    runtime = Interpreter()
    runtime.run(parse(source))
    return runtime.global_env


@pytest.mark.parametrize("expression,expected", [
    ('{"a": 1,}', {"a": 1}), ('{1, 2,}', {1, 2}),
    ('{1,}', {1}), ('{"a": {1,},}', {"a": {1}}),
    ('len([1, 2],)', 2), ('list(range(1, 3,),)', [1, 2]),
])
def test_trailing_commas(expression, expected):
    assert run("let result = " + expression + "\n").get("result") == expected


def test_multiline_parameters_defaults_calls_and_block_indentation():
    env = run('''fun build(
    first,
    values = {"key": {1, 2,},},
):
    return {"first": first, "values": values,}
let result = build(
    3,
)
let after = 4
''')
    assert env.get("result") == {"first": 3, "values": {"key": {1, 2}}}
    assert env.get("after") == 4


def test_variadic_parameter_and_call_trailing_comma():
    env = run('fun collect(first, ...rest,):\n    return rest\nlet result = collect(1, 2, 3,)\n')
    assert env.get("result") == [2, 3]


@pytest.mark.parametrize("source", [
    'let result = {,}\n', 'let result = {1,,}\n',
    'let result = {"a": 1,,}\n', 'let result = {"a":,}\n',
    'let result = len(,)\n', 'let result = len([1],,)\n',
    'fun bad(,):\n    return 1\n', 'fun bad(x,,):\n    return x\n',
    'let result = {1 2}\n', 'let result = len([1] 2,)\n',
])
def test_missing_or_doubled_values_are_rejected(source):
    with pytest.raises(SyntaxError):
        parse(source)
