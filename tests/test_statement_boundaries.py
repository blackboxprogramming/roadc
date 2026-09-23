"""Missing line separators must not silently become extra statements."""
import subprocess
import sys
from pathlib import Path

import pytest

from interpreter import Interpreter
from parser import parse


@pytest.mark.parametrize('source', [
    'let x = 1 let y = 2', 'let x = 1 2', '1 2', 'print(1) print(2)',
    'let x = 0\nx = 1 x = 2', 'let x = 0\nx += 1 x += 2',
    'fun f():\n    return 1 2\n', 'while true:\n    break print(1)\n',
    'for i in [1]:\n    continue print(1)\n',
    'module a module b', 'import a import b', 'export let x = 1 let y = 2',
])
def test_adjacent_statements_need_a_newline(source):
    with pytest.raises(SyntaxError, match=r'Expected end of statement at \d+:\d+'):
        parse(source)


def test_compound_statements_and_multiline_expressions_keep_boundaries():
    runtime = Interpreter()
    runtime.run(parse('''let result = []
fun f():
    if false:
        return 99
    elif true:
        result.append(
            1,
        )
    else:
        return 98
    for i in [2]:
        result.append(i)
    while false:
        break
    return
f()
result.append(3)'''))
    assert runtime.global_env.get('result') == [1, 2, 3]


def test_cli_rejects_whole_file_before_any_execution(tmp_path):
    source = tmp_path / 'adjacent.road'
    source.write_text('print("before")\nlet x = 1 print("after")\n')
    result = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1] / 'roadc.py'),
                             'run', str(source)], capture_output=True, text=True)
    assert result.returncode == 1
    assert result.stdout == ''
    assert 'Expected end of statement at 2:11' in result.stderr
