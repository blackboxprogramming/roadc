#!/usr/bin/env python3
"""
RoadC — The BlackRoad Language (Python interpreter)
Usage:
    roadc.py run <file.road>     Run a RoadC source file
    roadc.py repl                Interactive REPL
    roadc.py parse <file.road>   Parse and dump AST
    roadc.py check <files...>   Check syntax without running source
    roadc.py --check <files...> [--json]   Alias for check
    roadc.py version             Show version
"""

import argparse
import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

VERSION = "0.1.0"


class CheckParser(Parser):
    """Reject unfinished parser branches instead of looping on the same token."""

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


def check_file(path):
    """Return a syntax report. Never construct or run an Interpreter."""
    stage = "read"
    diagnostics = []
    try:
        with open(path, encoding="utf-8") as source:
            code = source.read()
        stage = "lex"
        tokens = Lexer(code).tokenize()
        stage = "parse"
        CheckParser(tokens).parse_program()
    except (OSError, UnicodeError, SyntaxError, ValueError, RecursionError) as error:
        line = column = None
        message = str(error)
        if isinstance(error, UnicodeError):
            diagnostic_code = "encoding_error"
        elif isinstance(error, OSError):
            diagnostic_code = "io_error"
        elif isinstance(error, RecursionError):
            diagnostic_code = "nesting_limit"
            message = "Source exceeds the parser nesting limit"
        else:
            diagnostic_code = "syntax_error"
            # Current lexer/parser errors carry their positions in the message.
            # Leave missing positions null; do not guess an editor location.
            location = re.search(r" at (\d+):(\d+)$", message)
            if location:
                line, column = map(int, location.groups())
        diagnostics.append({
            "code": diagnostic_code,
            "stage": stage,
            "severity": "error",
            "message": message,
            "line": line,
            "column": column,
        })
    return {"path": str(path), "ok": not diagnostics, "diagnostics": diagnostics}


def check_files(argv):
    arguments = argparse.ArgumentParser(
        prog="roadc.py check", allow_abbrev=False,
        description="Check UTF-8 Road source syntax without executing it.",
    )
    arguments.add_argument("files", nargs="+", metavar="FILE")
    arguments.add_argument("--json", action="store_true", help="emit one JSON report")
    options = arguments.parse_args(argv)
    files = [check_file(path) for path in options.files]
    report = {
        "schema_version": 1,
        "command": "check",
        "ok": all(item["ok"] for item in files),
        "files": files,
    }
    if options.json:
        print(json.dumps(report, ensure_ascii=True))
    else:
        for item in files:
            if item["ok"]:
                print(f"{item['path']}: syntax OK")
            for diagnostic in item["diagnostics"]:
                location = item["path"]
                if diagnostic["line"] is not None:
                    location += f":{diagnostic['line']}:{diagnostic['column']}"
                print(
                    f"{location}: error[{diagnostic['code']}]: {diagnostic['message']}",
                    file=sys.stderr,
                )
    return 0 if report["ok"] else 1


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
    if cmd in ('check', '--check'):
        sys.exit(check_files(sys.argv[2:]))
    elif cmd == 'version':
        print(f"RoadC {VERSION}")
    elif cmd == 'run' and len(sys.argv) > 2:
        run_file(sys.argv[2])
    elif cmd == 'parse' and len(sys.argv) > 2:
        parse_file(sys.argv[2])
    elif cmd == 'repl':
        repl()
    else:
        print(__doc__.strip())
        sys.exit(1)

if __name__ == '__main__':
    main()
