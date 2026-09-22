"""Numeric scanning preserves delimiters and reports source-level errors."""

import pytest

from lexer import Lexer, TokenType


@pytest.mark.parametrize("source, operator", [
    ("0..10", TokenType.DOUBLE_DOT),
    ("0...10", TokenType.TRIPLE_DOT),
    ("1.5..10", TokenType.DOUBLE_DOT),
])
def test_number_does_not_consume_dot_operator(source, operator):
    tokens = Lexer(source).tokenize()
    assert tokens[1].type == operator
    assert tokens[2].value == 10
    assert tokens[3].type == TokenType.EOF


@pytest.mark.parametrize("source", ["1e", "1E+", "1e-", "1.2e+", "1.2.3"])
def test_invalid_number_reports_position(source):
    with pytest.raises(SyntaxError, match="Invalid number at 1:9"):
        Lexer("let x = " + source).tokenize()


@pytest.mark.parametrize("source, value", [
    ("42", 42), ("1.", 1.0), ("3.14", 3.14),
    ("2e3", 2000.0), ("2E+3", 2000.0), ("2e-3", 0.002),
    ("1.25e2", 125.0),
])
def test_valid_number(source, value):
    tokens = Lexer(source).tokenize()
    assert tokens[0].value == value
    assert tokens[1].type == TokenType.EOF
