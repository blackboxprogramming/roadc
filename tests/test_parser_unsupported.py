"""All parser entry points must reject unfinished syntax without hanging."""

from pathlib import Path
import subprocess
import sys

import pytest

from parser import parse


CLI = Path(__file__).resolve().parents[1] / "roadc.py"


@pytest.mark.parametrize("command", ["run", "parse", "check"])
@pytest.mark.parametrize("program,location", [
    ("match value:\n    let x = 1\n", "1:1"),
    ("fun task():\n    spawn worker()\n", "2:5"),
    ("export spawn worker()\n", "1:8"),
])
def test_cli_rejects_unfinished_syntax(tmp_path, command, program, location):
    path = tmp_path / "unfinished.road"
    path.write_text(program)
    result = subprocess.run(
        [sys.executable, str(CLI), command, str(path)],
        capture_output=True, text=True, timeout=2,
    )
    assert result.returncode == 1
    assert "Unsupported statement" in result.stderr
    assert "at " + location in result.stderr
    assert result.stdout == ""


@pytest.mark.parametrize("program", ["match value:\n    let x = 1\n", "spawn worker()\n"])
def test_public_parser_rejects_unfinished_syntax(program):
    with pytest.raises(SyntaxError, match="Unsupported statement"):
        parse(program)


def test_repl_continues_after_unsupported_syntax():
    result = subprocess.run(
        [sys.executable, str(CLI), "repl"],
        input='spawn worker()\nprint("still running")\nexit\n',
        capture_output=True, text=True, timeout=2,
    )
    assert result.returncode == 0
    assert "Unsupported statement SPAWN at 1:1" in result.stdout
    assert "still running" in result.stdout
    assert result.stderr == ""
