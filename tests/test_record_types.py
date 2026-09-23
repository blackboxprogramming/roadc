"""Record syntax must lower to ordinary Road data, with no implicit authority."""

from pathlib import Path
import subprocess
import sys

import pytest

from ast_nodes import ListType, PrimitiveType, TypeDefinition
from interpreter import Interpreter
from parser import parse


def run(source):
    interpreter = Interpreter()
    interpreter.run(parse(source))
    return interpreter.global_env


DEVICE = '''type Device:
    name: string
    online: bool = false
    history: list[any] = []
'''


def test_documented_syntax_finishes_in_cli(tmp_path):
    source = tmp_path / "device.road"
    source.write_text(DEVICE + 'let device = Device{name: "Lucidia"}\nprint(device.name)\n')
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parents[1] / "roadc.py"),
         "run", str(source)],
        capture_output=True, text=True, timeout=5,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == "Lucidia\n"


def test_checked_in_record_example_runs_in_cli():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(root / "roadc.py"), "run",
         str(root / "examples" / "record_types.road")],
        capture_output=True, text=True, timeout=5,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == "Lucidia\nFalse\n1\n0\n"


def test_record_defaults_keep_short_circuit_evaluation():
    env = run('''let events = []
fun mark():
    events.append("called")
    return true
type Record:
    disabled: bool = false and mark()
    enabled: bool = true or mark()
let result = Record{}
''')
    assert env.get("result") == {"disabled": False, "enabled": True}
    assert env.get("events") == []


def test_record_compound_updates_evaluate_target_once():
    env = run('''let events = []
type Counter:
    count: int = 1
let counter = Counter{}
fun target():
    events.append("target")
    return counter
fun amount():
    events.append("amount")
    return 2
target().count += amount()
target()["count"] *= amount()
''')
    assert env.get("counter") == {"count": 6}
    assert env.get("events") == ["target", "amount", "target", "amount"]


def test_annotations_and_source_locations_survive_parsing():
    definition = parse(DEVICE).statements[0]
    assert isinstance(definition, TypeDefinition)
    assert definition.name == "Device"
    assert (definition.line, definition.column) == (1, 1)
    assert isinstance(definition.fields[0].type_annotation, PrimitiveType)
    assert definition.fields[0].type_annotation.name == "string"
    assert definition.fields[0].default_value is None
    assert definition.fields[0].line == 2
    assert isinstance(definition.fields[2].type_annotation, ListType)


def test_constructor_produces_plain_dictionary_with_defaults():
    env = run(DEVICE + 'let device = Device{name: "Lucidia"}\n')
    device = env.get("device")
    assert type(device) is dict
    assert device == {"name": "Lucidia", "online": False, "history": []}


def test_record_supports_existing_member_index_mutation_and_verbs():
    env = run(DEVICE + '''
fun rename(device, name):
    device.name = name
let device = Device{name: "Lucidia"}
rename(device, "Cecilia")
device["online"] = true
device.history.append("renamed")
let names = device.keys()
let direct = Device{name: "Octavia"}.name
''')
    assert env.get("device") == {
        "name": "Cecilia", "online": True, "history": ["renamed"],
    }
    assert set(env.get("names")) == {"name", "online", "history"}
    assert env.get("direct") == "Octavia"


def test_multiline_nested_constructor_inside_function_preserves_blocks():
    env = run(DEVICE + '''
type Fleet:
    device: Device
    label: string
fun make_fleet():
    let result = Fleet{
        device: Device{
            name: "Lucidia",
            history: [
                "observed",
            ],
        },
        # this is a comment inside the constructor

        label: "home",
    }
    result.device.online = true
    return result
let fleet = make_fleet()
let after = 1729
''')
    assert env.get("fleet") == {
        "device": {"name": "Lucidia", "online": True, "history": ["observed"]},
        "label": "home",
    }
    assert env.get("after") == 1729


def test_mutable_literal_defaults_are_evaluated_for_each_record():
    env = run(DEVICE + '''
let first = Device{name: "Lucidia"}
let second = Device{name: "Octavia"}
first.history.append("seen")
''')
    assert env.get("first")["history"] == ["seen"]
    assert env.get("second")["history"] == []


def test_constructor_aliases_capture_each_definition_environment():
    env = run('''fun make_type(label):
    type Device:
        name: string = label
    return Device
let First = make_type("Lucidia")
let Second = make_type("Octavia")
let first = First{}
let second = Second{}
''')
    assert env.get("first") == {"name": "Lucidia"}
    assert env.get("second") == {"name": "Octavia"}


def test_explicit_values_use_caller_scope_defaults_use_definition_scope():
    env = run('''let label = "definition"
type Record:
    supplied: string
    fallback: string = label
fun build():
    let label = "caller"
    return Record{supplied: label}
let result = build()
''')
    assert env.get("result") == {"supplied": "caller", "fallback": "definition"}


def test_explicit_values_then_omitted_defaults_run_once_in_order():
    env = run('''let events = []
fun mark(value):
    events.append(value)
    return value
type Record:
    first: string = mark("first default")
    second: string = mark("unused default")
    third: string = mark("third default")
let result = Record{second: mark("explicit")}
''')
    assert env.get("events") == ["explicit", "first default", "third default"]


@pytest.mark.parametrize("literal, message", [
    ('Device{}', "Missing required field.*name"),
    ('Device{name: mark(), extra: mark()}', "Unknown field.*extra"),
    ('Device{online: mark()}', "Missing required field.*name"),
])
def test_shape_errors_precede_value_or_default_evaluation(literal, message):
    interpreter = Interpreter()
    program = parse('''let events = []
fun mark():
    events.append("evaluated")
    return true
type Device:
    name: string
    online: bool = mark()
let result = ''' + literal + '\n')
    with pytest.raises(TypeError, match=message):
        interpreter.run(program)
    assert interpreter.global_env.get("events") == []


@pytest.mark.parametrize("source, message", [
    ('type Bad:\n    name: string\n    name: int\n', "Duplicate field.*name"),
    ('let value = Device{name: 1, name: 2}\n', "Duplicate field.*name"),
    ('type Bad:\n    name string\n', "Expected COLON"),
    ('type Bad:\n    name: string other: int\n', "Expected newline"),
    ('type Bad:\n    name: string =\n', "Unexpected token"),
    ('type Empty:\n', "Expected INDENT"),
    ('let value = Device{name: 1 online: true}\n', "Expected COMMA"),
    ('let value = Device{name: }\n', "Unexpected token"),
    ('let value = Device{"name": 1}\n', "Expected IDENTIFIER"),
])
def test_malformed_records_fail_with_syntax_errors(source, message):
    with pytest.raises(SyntaxError, match=message):
        parse(source)


@pytest.mark.parametrize("source, message", [
    ('let value = Device{name: "Lucidia"', "Unclosed delimiter"),
    ('let value = Device{name: "Lucidia"]', "Mismatched delimiter"),
    ('let value = 1}', "Unexpected closing delimiter"),
])
def test_bad_constructor_delimiters_fail_without_hanging(source, message):
    with pytest.raises(SyntaxError, match=message):
        parse(source)


def test_constructor_requires_a_declared_type():
    with pytest.raises(NameError, match="Undefined variable 'Missing'"):
        run('let value = Missing{}\n')
    with pytest.raises(TypeError, match="not a record type"):
        run('let Device = {}\nlet value = Device{}\n')


def test_annotations_remain_metadata_as_in_existing_interpreter():
    env = run('''type Label:
    value: string
let label = Label{value: 1729}
label.value = false
''')
    assert env.get("label") == {"value": False}


def test_route_and_permission_fields_remain_plain_data():
    env = run('''type Request:
    route: string
    permissions: set[string]
    authorized: bool = false
    executed: bool = false
let request = Request{
    route: "road://devices/lucidia",
    permissions: {"start"},
}
''')
    assert env.get("request") == {
        "route": "road://devices/lucidia", "permissions": {"start"},
        "authorized": False, "executed": False,
    }


def test_records_work_with_existing_permission_checked_object_verbs():
    from tests.test_road_objects import RUNTIME

    env = run(RUNTIME + DEVICE + '    permissions: set[string]\n' + '''
let device = Device{name: "Lucidia", permissions: {"status"}}
let denied = dispatch("start", device)
let before = len(device.history)
let observed = dispatch("status", device)
''')
    assert env.get("denied") == "permission denied"
    assert env.get("before") == 0
    assert env.get("observed") == "offline"
    assert env.get("device")["online"] is False
    assert env.get("device")["history"] == [
        {"device": "Lucidia", "action": "status", "online": False},
    ]


def test_shared_default_references_are_not_implicitly_copied():
    env = run('''let shared = []
type Record:
    history: list[any] = shared
let first = Record{}
let second = Record{}
first.history.append("shared")
''')
    assert env.get("second")["history"] == ["shared"]
    assert env.get("first")["history"] is env.get("shared")


def test_defaults_observe_live_bindings_without_injecting_field_locals():
    env = run('''let label = "old"
type Record:
    label: string = "field"
    outer: string = label
label = "new"
let result = Record{}
''')
    assert env.get("result") == {"label": "field", "outer": "new"}


def test_multiline_grouping_preserves_existing_expressions_and_indentation():
    env = run('''fun build():
    let result = {
        "numbers": [
            1,
            2
        ],
        "sum": (
            1 +
            2
        )
    }
    return result
let result = build()
''')
    assert env.get("result") == {"numbers": [1, 2], "sum": 3}
