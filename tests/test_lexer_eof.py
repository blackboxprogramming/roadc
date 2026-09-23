"""End-of-file input must finish cleanly or report a Road syntax error."""

import pytest

from lexer import Lexer, TokenType


@pytest.mark.parametrize("suffix", [" ", "\t", "\r", " \t\r"])
def test_trailing_whitespace_preserves_tokens(suffix):
    expected = Lexer("let x = 42").tokenize()
    actual = Lexer("let x = 42" + suffix).tokenize()
    assert [(t.type, t.value) for t in actual] == [
        (t.type, t.value) for t in expected
    ]


@pytest.mark.parametrize("source", [" ", "\t", "\r", " \t\r"])
def test_whitespace_only_file(source):
    assert [t.type for t in Lexer(source).tokenize()] == [TokenType.EOF]


@pytest.mark.parametrize("quote", ["'", '"'])
def test_unfinished_escape_reports_string_start(quote):
    with pytest.raises(SyntaxError, match="Unterminated string at 1:9"):
        Lexer("let x = " + quote + "hello" + "\\").tokenize()


def test_escaped_backslash_at_end_of_valid_string():
    tokens = Lexer('"hello' + "\\\\" + '"').tokenize()
    assert tokens[0].value == "hello" + "\\"


def test_skip_newlines_stops_at_eof():
    lexer = Lexer(" \n\t\r")
    lexer.skip_whitespace(skip_newlines=True)
    assert lexer.current_char() is None
