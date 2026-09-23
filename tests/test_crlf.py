"""Raw CRLF input must retain block structure across blank lines."""
import pytest

from interpreter import Interpreter
from lexer import Lexer
from parser import parse


@pytest.mark.parametrize('blank', ['', ' ', '    ', '\t'])
@pytest.mark.parametrize('newline', ['\r\n', 'mixed'])
def test_blank_lines_preserve_block_tokens_and_execution(blank, newline):
    source = ('let result = []\nif true:\n    result.append(1)\n' + blank + '\n'
              '    if true:\n        result.append(2)\n' + blank + '\n'
              '        result.append(3)\n    result.append(4)\nresult.append(5)\n')
    if newline == 'mixed':
        raw = ''.join(line + ('\r\n' if n % 2 else '\n')
                      for n, line in enumerate(source.splitlines()))
    else:
        raw = source.replace('\n', newline)
    assert Lexer(raw).tokenize() == Lexer(source).tokenize()
    runtime = Interpreter()
    runtime.run(parse(raw))
    assert runtime.global_env.get('result') == [1, 2, 3, 4, 5]


def test_crlf_inside_string_is_not_normalized():
    runtime = Interpreter()
    runtime.run(parse('let result = "a\r\nb"\r\n'))
    assert runtime.global_env.get('result') == 'a\r\nb'


def test_crlf_grouping_and_comments_preserve_outer_block():
    source = ('if true:\n    let result = [\n        1,\n\n        2,\n    ]\n'
              '    # comment\n\n    result.append(3)\n')
    runtime = Interpreter()
    runtime.run(parse(source.replace('\n', '\r\n')))
    assert runtime.global_env.get('result') == [1, 2, 3]
