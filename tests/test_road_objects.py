"""Tests for composing Road objects from RoadC collection primitives."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from interpreter import Interpreter
from lexer import Lexer
from parser import Parser


RUNTIME = r'''
fun make_device(name, kind, permissions):
    let device = {"name": name, "kind": kind, "online": false, "permissions": permissions, "identity": (name, kind), "history": []}
    return device

fun has_permission(device, action):
    for permission in device.permissions:
        if permission == action:
            return true
    return false

fun record(device, action):
    let event = {"device": device.name, "action": action, "online": device.online}
    device.history.append(event)
    return event

fun start(device):
    if not has_permission(device, "start"):
        return "permission denied"
    device.online = true
    record(device, "start")
    return "started"

fun stop(device):
    if not has_permission(device, "stop"):
        return "permission denied"
    device.online = false
    record(device, "stop")
    return "stopped"

fun status(device):
    record(device, "status")
    if device.online:
        return "online"
    return "offline"

let actions = {"start": start, "stop": stop, "status": status}

fun dispatch(action, device):
    let handler = actions[action]
    return handler(device)
'''


def run(source: str) -> Interpreter:
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse_program()
    interpreter = Interpreter()
    interpreter.run(program)
    return interpreter


def test_device_is_composed_from_native_collections():
    source = RUNTIME + r'''
let lucidia = make_device("Lucidia", "Raspberry Pi", {"start", "stop", "status"})
'''
    interpreter = run(source)
    lucidia = interpreter.global_env.get("lucidia")

    assert lucidia["name"] == "Lucidia"
    assert lucidia["kind"] == "Raspberry Pi"
    assert lucidia["online"] is False
    assert lucidia["identity"] == ("Lucidia", "Raspberry Pi")
    assert lucidia["permissions"] == {"start", "stop", "status"}
    assert lucidia["history"] == []


def test_action_dict_dispatches_functions_and_records_history():
    source = RUNTIME + r'''
let lucidia = make_device("Lucidia", "Raspberry Pi", {"start", "stop", "status"})
let started = dispatch("start", lucidia)
let online_after_start = lucidia.online
let current = dispatch("status", lucidia)
let stopped = dispatch("stop", lucidia)
let online_after_stop = lucidia.online
'''
    interpreter = run(source)
    lucidia = interpreter.global_env.get("lucidia")

    assert interpreter.global_env.get("started") == "started"
    assert interpreter.global_env.get("online_after_start") is True
    assert interpreter.global_env.get("current") == "online"
    assert interpreter.global_env.get("stopped") == "stopped"
    assert interpreter.global_env.get("online_after_stop") is False
    assert [event["action"] for event in lucidia["history"]] == [
        "start",
        "status",
        "stop",
    ]


def test_permissions_are_data_not_hidden_runtime_state():
    source = RUNTIME + r'''
let alexandria = make_device("Alexandria", "Mac", {"status"})
let result = dispatch("start", alexandria)
'''
    interpreter = run(source)
    alexandria = interpreter.global_env.get("alexandria")

    assert interpreter.global_env.get("result") == "permission denied"
    assert alexandria["online"] is False
    assert alexandria["history"] == []
