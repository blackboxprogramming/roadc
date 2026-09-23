"""Real REPL sessions preserve bindings and execute complete input blocks."""

from pathlib import Path
import subprocess
import sys
from unittest import mock

import roadc


CLI = Path(__file__).resolve().parents[1] / "roadc.py"


def session(source):
    result = subprocess.run([sys.executable, str(CLI), "repl"], input=source,
                            capture_output=True, text=True, timeout=5)
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    return result.stdout


def test_function_definition_then_builtin_callback_in_same_session():
    output = session('fun double(value):\n    return value * 2\n\n'
                     'print(map(double, [2, 3]))\nexit\n')
    assert "[4, 6]" in output
    assert "Error:" not in output


def test_loop_and_nested_conditionals_wait_for_blank_line():
    output = session('let values = []\nfor x in 0..4:\n'
                     '    if x == 1:\n        continue\n'
                     '    elif x == 2:\n        values.append(20)\n'
                     '    else:\n        values.append(x)\n\n'
                     'print(values)\nquit\n')
    assert "[0, 20, 3]" in output
    assert "Error:" not in output


def test_block_header_with_trailing_comment():
    output = session('if true: # choose a branch\n    print("chosen")\n\nexit\n')
    assert "chosen" in output
    assert "Error:" not in output


def test_colons_in_strings_and_comments_do_not_request_a_block():
    output = session('print("colon:")\n# ordinary comment:\nprint("after")\nexit\n')
    assert "colon:" in output and "after" in output
    assert "....> " not in output
    assert "Error:" not in output


def test_parse_error_in_block_does_not_run_earlier_body_statements():
    output = session('let seen = []\nif true:\n    seen.append(1)\n    let = 3\n\n'
                     'print(seen)\nexit\n')
    assert "Error:" in output
    assert "[]" in output


def test_eof_discards_unsubmitted_block():
    output = session('if true:\n    print("MUST NOT RUN")\n')
    assert "MUST NOT RUN" not in output
    assert "Error:" not in output


def test_ctrl_c_discards_block_and_keeps_previous_bindings(capsys):
    inputs = ['let value = 7', 'if true:', '    value = 99', KeyboardInterrupt(),
              'print(value)', 'exit']
    with mock.patch('builtins.input', side_effect=inputs):
        roadc.repl()
    output = capsys.readouterr().out
    assert "7\n" in output
    assert "99" not in output
    assert "Error:" not in output


def test_ctrl_c_at_primary_prompt_keeps_session_usable(capsys):
    with mock.patch('builtins.input', side_effect=[KeyboardInterrupt(), 'print(8)', 'exit']):
        roadc.repl()
    assert "8\n" in capsys.readouterr().out


def test_runtime_failure_preserves_prior_state_and_accepts_next_input():
    output = session('let seen = []\nif true:\n    seen.append(1)\n    missing()\n\n'
                     'print(seen)\nexit\n')
    assert "Error:" in output
    assert "[1]" in output


def test_single_line_commands_and_blank_input_still_work():
    output = session('\nlet value = 2\nvalue += 3\nprint(value)\nexit\n')
    assert "5\n" in output
    assert "Error:" not in output


def test_interrupt_during_execution_keeps_already_performed_effects(capsys):
    inputs = ['let seen = []', 'if true:', '    seen.append(1)',
              '    input("interrupt")', '', KeyboardInterrupt(), 'print(seen)', 'exit']
    with mock.patch('builtins.input', side_effect=inputs):
        roadc.repl()
    output = capsys.readouterr().out
    assert "[1]\n" in output
    assert "Error:" not in output


def test_record_definition_and_constructor_persist():
    output = session('type Task:\n    count: int = 3\n\n'
                     'let task = Task{}\nprint(task.count)\nexit\n')
    assert "3\n" in output
    assert "Error:" not in output


def test_empty_block_reports_error_and_next_command_runs():
    output = session('if true:\n\nprint("recovered")\nexit\n')
    assert "Error:" in output
    assert "recovered" in output
