"""CLI consumers need reliable exit codes and concise source diagnostics."""

from pathlib import Path
import subprocess
import sys

import pytest


CLI = Path(__file__).resolve().parents[1] / "roadc.py"


def invoke(*args):
    return subprocess.run([sys.executable, str(CLI), *map(str, args)],
                          capture_output=True, text=True, timeout=5)


@pytest.mark.parametrize("command", ["run", "parse"])
@pytest.mark.parametrize("content", [b'let = 1\n', b'\xff', None])
def test_source_errors_are_concise(tmp_path, command, content):
    source = tmp_path / "bad.road"
    if content is not None:
        source.write_bytes(content)
    result = invoke(command, source)
    assert result.returncode == 1
    assert str(source) in result.stderr
    assert "error:" in result.stderr
    assert "Traceback" not in result.stderr
    assert result.stdout == ""


@pytest.mark.parametrize("program,message", [
    ('let x = 1 / 0\n', "division by zero"),
    ('missing()\n', "Undefined variable"),
    ('let values = [1]\nprint(values[9])\n', "out of range"),
    ('spawn worker()\n', "Unsupported statement SPAWN"),
    ('import missing\n', "Unsupported statement"),
])
def test_runtime_errors_have_failure_exit_without_traceback(tmp_path, program, message):
    source = tmp_path / "failure.road"
    source.write_text(program)
    result = invoke("run", source)
    assert result.returncode == 1
    assert message in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("command", ["run", "parse"])
def test_extra_arguments_do_not_execute_source(tmp_path, command):
    source = tmp_path / "program.road"
    source.write_text('print("MUST NOT RUN")\n')
    result = invoke(command, source, "extra")
    assert result.returncode == 2
    assert "usage:" in result.stderr
    assert result.stdout == ""


@pytest.mark.parametrize("command", ["run", "parse"])
def test_missing_path_is_usage_error(command):
    result = invoke(command)
    assert result.returncode == 2
    assert "usage:" in result.stderr
    assert result.stdout == ""


def test_output_before_runtime_error_is_preserved(tmp_path):
    source = tmp_path / "partial.road"
    source.write_text('print("before")\nlet x = 1 / 0\nprint("after")\n')
    result = invoke("run", source)
    assert result.returncode == 1
    assert result.stdout == "before\n"
    assert "division by zero" in result.stderr


@pytest.mark.parametrize("program,error_class", [
    ('let record = {}\nrecord.missing += 1\n', "KeyError"),
    ('let value = 1 / 0\n', "ZeroDivisionError"),
    ('missing()\n', "NameError"),
])
def test_concise_errors_preserve_exception_class_for_receipt_consumers(tmp_path, program, error_class):
    source = tmp_path / "failure.road"
    source.write_text(program, encoding="utf-8")
    result = invoke("run", source)
    assert result.returncode == 1
    assert f"{source}: error: {error_class}: " in result.stderr
    assert "Traceback" not in result.stderr
