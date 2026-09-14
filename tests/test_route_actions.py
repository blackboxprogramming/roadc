"""Contract tests for Road v0.1 Route-addressed action envelopes."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from interpreter import Interpreter
from lexer import Lexer
from parser import Parser


def run(source: str) -> Interpreter:
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse_program()
    interpreter = Interpreter()
    interpreter.run(program)
    return interpreter


def test_route_action_envelope_is_plain_road_data():
    source = r'''
fun action(actor, verb, target, input):
    return {"version": "road-action/0.1", "actor": actor, "action": verb, "target": target, "input": input}

let target = "road://self/roadies/lucidia"
let request = action("alexa", "ask", target, {"prompt": "hello"})
'''
    interpreter = run(source)
    request = interpreter.global_env.get("request")

    assert request == {
        "version": "road-action/0.1",
        "actor": "alexa",
        "action": "ask",
        "target": "road://self/roadies/lucidia",
        "input": {"prompt": "hello"},
    }


def test_route_is_identity_not_permission():
    source = r'''
let route = "road://self/devices/octavia"
let permissions = {"status"}
'''
    interpreter = run(source)

    assert interpreter.global_env.get("route") == "road://self/devices/octavia"
    assert interpreter.global_env.get("permissions") == {"status"}
