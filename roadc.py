#!/usr/bin/env python3
"""
RoadC — The BlackRoad Language (Python interpreter)
Usage:
    roadc.py run <file.road>     Run a RoadC source file
    roadc.py repl                Interactive REPL
    roadc.py parse <file.road>   Parse and dump AST
    roadc.py check <file.road>   Check syntax without executing the program
    roadc.py version             Show version
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

VERSION = "0.1.0"

class CheckParser(Parser):
    """Reject unfinished statement parsers that do not consume their token."""

    def parse_statement(self):
        self.skip_newlines()
        start = self.pos
        token = self.current_token()
        statement = super().parse_statement()
        if self.pos == start:
            raise SyntaxError(
                f"Unsupported statement {token.type.name} at {token.line}:{token.column}"
            )
        return statement

def run_code(code):
    tokens = Lexer(code).tokenize()
    ast = Parser(tokens).parse_program()
    Interpreter().run(ast)

def run_file(path):
    with open(path) as f:
        run_code(f.read())

def parse_file(path):
    with open(path) as f:
        code = f.read()
    tokens = Lexer(code).tokenize()
    ast = Parser(tokens).parse_program()
    for stmt in ast.statements:
        print(stmt)

def check_file(path):
    """Parse a UTF-8 source file without constructing or running an interpreter."""
    with open(path, encoding="utf-8") as source:
        code = source.read()
    return CheckParser(Lexer(code).tokenize()).parse_program()

def repl():
    print(f"RoadC {VERSION} — type 'exit' to quit")
    interp = Interpreter()
    while True:
        try:
            line = input("road> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.strip() in ('exit', 'quit'):
            break
        if not line.strip():
            continue
        try:
            tokens = Lexer(line).tokenize()
            ast = Parser(tokens).parse_program()
            interp.run(ast)
        except Exception as e:
            print(f"Error: {e}")

def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == 'version':
        print(f"RoadC {VERSION}")
    elif cmd == 'run' and len(sys.argv) > 2:
        run_file(sys.argv[2])
    elif cmd == 'parse' and len(sys.argv) > 2:
        parse_file(sys.argv[2])
    elif cmd == 'check' and len(sys.argv) == 3:
        path = sys.argv[2]
        try:
            check_file(path)
        except (OSError, UnicodeError, SyntaxError, ValueError, RecursionError) as exc:
            print(f"{path}: {exc}", file=sys.stderr)
            sys.exit(1)
        print(f"Syntax OK: {path}")
    elif cmd == 'repl':
        repl()
    else:
        print(__doc__.strip())
        sys.exit(1)

if __name__ == '__main__':
    main()
