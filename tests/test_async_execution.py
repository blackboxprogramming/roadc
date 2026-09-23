"""Parsed concurrency syntax must not masquerade as synchronous execution."""

import json
from pathlib import Path
import subprocess
import sys

import pytest

from interpreter import Interpreter
from parser import parse


def test_async_declaration_fails_before_binding_or_body_effects():
    runtime = Interpreter()
    with pytest.raises(RuntimeError, match=r"Unsupported async function task at 2:1"):
        runtime.run(parse('''let events = []
async fun task():
    events.append("body")
task()
'''))
    assert runtime.global_env.get("events") == []
    with pytest.raises(NameError):
        runtime.global_env.get("task")


def test_await_fails_before_evaluating_its_operand():
    runtime = Interpreter()
    with pytest.raises(RuntimeError, match=r"Unsupported await expression at 5:14"):
        runtime.run(parse('''let events = []
fun task():
    events.append("body")
    return 1
let result = await task()
'''))
    assert runtime.global_env.get("events") == []


def test_unreached_async_syntax_has_no_runtime_effect():
    runtime = Interpreter()
    runtime.run(parse('''if false:
    async fun unused():
        return 1
let guarded = false and await missing()
'''))
    assert runtime.global_env.get("guarded") is False


def test_syntax_check_accepts_async_but_run_reports_unsupported(tmp_path):
    source = tmp_path / "async.road"
    source.write_text('async fun task():\n    return 1\ntask()\n')
    cli = Path(__file__).resolve().parents[1] / "roadc.py"
    checked = subprocess.run([sys.executable, str(cli), "check", str(source), "--json"],
                             capture_output=True, text=True, timeout=5)
    assert checked.returncode == 0
    assert json.loads(checked.stdout)["ok"] is True
    executed = subprocess.run([sys.executable, str(cli), "run", str(source)],
                              capture_output=True, text=True, timeout=5)
    assert executed.returncode == 1
    assert "Unsupported async function" in executed.stderr
    assert "Traceback" not in executed.stderr
    assert executed.stdout == ""
