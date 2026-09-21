import subprocess
import sys
from pathlib import Path


CLI = Path(__file__).resolve().parents[1] / 'roadc.py'


def invoke(*args):
    return subprocess.run([sys.executable, str(CLI), *map(str, args)],
                          capture_output=True, text=True, timeout=10)


def test_check_parses_without_executing(tmp_path):
    source = tmp_path / 'safe.road'
    source.write_text('print("MUST NOT EXECUTE")\nlet x = 1 / 0\n')
    result = invoke('check', source)
    assert result.returncode == 0
    assert 'MUST NOT EXECUTE' not in result.stdout
    assert 'Syntax OK' in result.stdout
    assert result.stderr == ''
    assert list(tmp_path.iterdir()) == [source]


def test_check_invalid_syntax_has_diagnostic_and_failure_exit(tmp_path):
    source = tmp_path / 'broken.road'
    source.write_text('let x =\n')
    result = invoke('check', source)
    assert result.returncode == 1
    assert str(source) in result.stderr
    assert 'Traceback' not in result.stderr
    assert 'Syntax OK' not in result.stdout


def test_check_missing_file_is_a_clean_error(tmp_path):
    source = tmp_path / 'missing.road'
    result = invoke('check', source)
    assert result.returncode == 1
    assert str(source) in result.stderr
    assert 'Traceback' not in result.stderr


def test_check_rejects_extra_arguments(tmp_path):
    source = tmp_path / 'ok.road'
    source.write_text('let x = 1\n')
    result = invoke('check', source, 'ignored')
    assert result.returncode != 0
    assert 'Syntax OK' not in result.stdout


def test_check_rejects_non_utf8_source(tmp_path):
    source = tmp_path / 'invalid.road'
    source.write_bytes(b'\xff')
    result = invoke('check', source)
    assert result.returncode == 1
    assert str(source) in result.stderr
    assert 'Traceback' not in result.stderr
