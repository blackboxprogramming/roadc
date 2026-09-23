"""Exercise the syntax checker through the real command-line entry point."""

import json
from pathlib import Path
import subprocess
import sys

import pytest


CLI = Path(__file__).resolve().parents[1] / "roadc.py"


def invoke(*args):
    return subprocess.run(
        [sys.executable, str(CLI), *map(str, args)],
        capture_output=True, text=True, timeout=5,
    )


@pytest.fixture
def source(tmp_path):
    def write(text, name="program.road"):
        path = tmp_path / name
        path.write_text(text, encoding="utf-8")
        return path
    return write


@pytest.mark.parametrize("command", ["check", "--check"])
def test_check_never_executes_program(source, command):
    path = source('print("SHOULD NOT RUN")\ninput("PROMPT")\nlet x = 1 / 0\n')
    result = invoke(command, path)
    assert result.returncode == 0
    assert result.stdout == f"{path}: syntax OK\n"
    assert result.stderr == ""


def test_check_does_not_run_infinite_loop(source):
    path = source("while true:\n    print(1)\n")
    result = invoke("--check", path, "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout)["ok"] is True


def test_json_success_contract_is_syntax_only(source):
    path = source('let message = "Olá 道"\nmissing_function(message)\n')
    result = invoke("check", "--json", path)
    assert result.returncode == 0
    assert result.stderr == ""
    assert json.loads(result.stdout) == {
        "schema_version": 1,
        "command": "check",
        "ok": True,
        "files": [{"path": str(path), "ok": True, "diagnostics": []}],
    }


@pytest.mark.parametrize("program,stage,line,column", [
    ("let x = 1\n`\n", "lex", 2, 1),
    ("let = 1\n", "parse", 1, 5),
    ('let x = "unterminated', "lex", 1, 9),
])
def test_json_syntax_error_has_phase_and_location(source, program, stage, line, column):
    path = source(program)
    result = invoke("check", path, "--json")
    assert result.returncode == 1
    assert result.stderr == ""
    report = json.loads(result.stdout)
    assert report["ok"] is False
    assert report["files"][0]["ok"] is False
    diagnostic, = report["files"][0]["diagnostics"]
    assert diagnostic == {
        "code": "syntax_error", "stage": stage, "severity": "error",
        "message": diagnostic["message"], "line": line, "column": column,
    }
    assert diagnostic["message"]
    assert "Traceback" not in result.stdout


def test_text_error_uses_stderr(source):
    path = source("let = 1\n")
    result = invoke("--check", path)
    assert result.returncode == 1
    assert result.stdout == ""
    assert f"{path}:1:5: error[syntax_error]" in result.stderr
    assert "Expected IDENTIFIER" in result.stderr
    assert "Traceback" not in result.stderr


def test_batch_preserves_order_and_continues_after_failure(source, tmp_path):
    missing = tmp_path / "missing.road"
    invalid = source("let = 1\n", "invalid.road")
    valid = source("", "empty.road")
    result = invoke("check", missing, invalid, valid, "--json")
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["ok"] is False
    assert [item["path"] for item in report["files"]] == list(map(str, [missing, invalid, valid]))
    assert [item["ok"] for item in report["files"]] == [False, False, True]
    diagnostic = report["files"][0]["diagnostics"][0]
    assert diagnostic["code"] == "io_error"
    assert diagnostic["stage"] == "read"
    assert diagnostic["line"] is None
    assert diagnostic["column"] is None


def test_invalid_utf8_is_a_read_diagnostic(tmp_path):
    path = tmp_path / "invalid.road"
    path.write_bytes(b"\xff\xfe")
    result = invoke("check", path, "--json")
    assert result.returncode == 1
    diagnostic = json.loads(result.stdout)["files"][0]["diagnostics"][0]
    assert diagnostic["code"] == "encoding_error"
    assert diagnostic["stage"] == "read"
    assert diagnostic["line"] is None
    assert diagnostic["column"] is None


def test_malformed_number_has_a_located_diagnostic(source):
    result = invoke("check", source("let x = 1.2.3\n"), "--json")
    assert result.returncode == 1
    diagnostic = json.loads(result.stdout)["files"][0]["diagnostics"][0]
    assert diagnostic["code"] == "syntax_error"
    assert diagnostic["stage"] == "lex"
    assert diagnostic["line"] == 1
    assert diagnostic["column"] == 9


@pytest.mark.parametrize("program", [
    "match value:\n    let x = 1\n",
    "fun task():\n    spawn worker()\n",
    "export match value:\n    let x = 1\n",
    "export spawn worker()\n",
])
def test_unimplemented_statements_fail_promptly(source, program):
    result = invoke("check", source(program), "--json")
    assert result.returncode == 1
    diagnostic = json.loads(result.stdout)["files"][0]["diagnostics"][0]
    assert diagnostic["code"] == "syntax_error"
    assert diagnostic["stage"] == "parse"
    assert "Unsupported statement" in diagnostic["message"]


def test_excessive_nesting_is_a_diagnostic(source):
    result = invoke("check", source("let x = " + "(" * 1500 + "1" + ")" * 1500), "--json")
    assert result.returncode == 1
    diagnostic = json.loads(result.stdout)["files"][0]["diagnostics"][0]
    assert diagnostic["code"] == "nesting_limit"
    assert diagnostic["stage"] == "parse"


@pytest.mark.parametrize("args", [("check",), ("--check",), ("check", "--typo")])
def test_bad_check_usage_returns_two(args):
    result = invoke(*args)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "usage:" in result.stderr


def test_existing_run_and_parse_commands_still_work(source):
    path = source('print("hello")\n')
    run = invoke("run", path)
    assert run.returncode == 0
    assert run.stdout == "hello\n"
    parsed = invoke("parse", path)
    assert parsed.returncode == 0
    assert "ExpressionStatement" in parsed.stdout
    assert invoke("version").stdout.startswith("RoadC ")


@pytest.mark.parametrize("prefix", ["", "export "])
def test_check_accepts_records_without_evaluating_defaults(source, prefix):
    path = source(prefix + 'type Device:\n    name: string = input("PROMPT")\n'
                  'let device = Device{}\n')
    result = invoke("check", path, "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout)["files"] == [
        {"path": str(path), "ok": True, "diagnostics": []},
    ]
    assert result.stderr == ""


def test_checked_in_examples_pass_batch_check():
    root = CLI.parent
    paths = [root / "examples" / name for name in (
        "demo.road", "road_objects.road", "route_actions.road", "record_types.road",
        "ranges.road",
    )]
    result = invoke("check", *paths, "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout)["files"] == [
        {"path": str(path), "ok": True, "diagnostics": []} for path in paths
    ]
    assert result.stderr == ""


@pytest.mark.parametrize("program", [" \t\r", "let values = 0..3 \t"])
def test_check_accepts_trailing_whitespace(source, program):
    result = invoke("check", source(program), "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout)["ok"] is True
    assert result.stderr == ""


def test_checked_in_range_example_runs():
    result = invoke("run", CLI.parent / "examples" / "ranges.road")
    assert result.returncode == 0
    assert result.stdout == "0\n1\n2\n3\n"
    assert result.stderr == ""
