# Python execution support

The Python interpreter executes compound assignment (`+=`, `-=`, `*=`, `/=`)
on variables, list/dictionary indexes, and dictionary dot members. The object
and index are evaluated once, then the current value is read, then the right
operand is evaluated and the result stored. Missing keys and invalid indexes
raise errors rather than inserting an invented initial value.

```road
let queue = [0]
let agent = {"completed": 0}
for task in [2, 3, 5]:
    queue[0] += task
    agent.completed += 1
print(queue[0], agent.completed)  # 10 3
```

The example updates local data; it does not dispatch agents or call providers.

Parsed but unsupported statements now raise `RuntimeError` with the statement
kind and source position. In particular, module declarations, imports, exports,
and spatial definitions are not executable Python-runtime features. Parsing
them does not mean they ran. Invalid assignment targets also fail explicitly.
Execution stops at the error; earlier side effects are not rolled back.

`async fun` and `await` are parsed syntax, but the interpreter does not provide
an async scheduler. Reaching an async declaration raises a located runtime
error before binding its name; reaching `await` raises before evaluating its
operand. Async functions are not silently executed synchronously. Unreached
branches and short-circuit operands remain unevaluated. `check` validates syntax
only and can accept these forms; its success does not establish async support.
The unfinished `spawn` syntax is rejected by the parser.

RoadOS uses the process exit code to classify a run receipt. This failure
behavior prevents an ignored import or export from appearing as a completed
workspace run. Run the companion check in the RoadOS repository:

```bash
ROAD_TEST_ROADC="$PWD/../roadc" python3 -m unittest discover \
  -s tests -p test_roadc_execution_integration.py -v
```

Only opt in with a trusted checkout: RoadOS runs the selected runtime's code.
These checks cover the Python implementation, not C compiler parity.

## CLI failure reporting

`python3 roadc.py run FILE` and `parse FILE` require exactly one UTF-8 source
file. Missing or extra arguments exit 2 with usage on stderr before reading or
executing source. Successful commands exit 0. File, encoding, syntax and expected
runtime errors exit 1 with `FILE: error: ERROR_CLASS: MESSAGE` on stderr, without a Python
traceback. Lexer/parser source locations remain in the message where available;
runtime errors do not yet consistently carry Road source positions.

Program output before a runtime failure remains on stdout, and earlier effects
are not rolled back. Exit 1 must not be treated as successful completion just
because some output exists. `parse` never executes the source. Imported Python
APIs continue to raise their original exceptions, which preserves traceback
access for developers. Structured syntax diagnostics remain available through
`check --json`.

## Verify RoadC through RoadOS receipts

The RoadC suite also includes opt-in tests that launch the real RoadOS workspace
runner against this interpreter, then verify its saved receipts:

```bash
ROAD_TEST_ROADOS=/absolute/path/to/RoadOS python3 -m pytest tests/test_builtin_workspace.py -q
```

Choose a trusted checkout: the test executes its `workspace.py`. Each case uses
a temporary local project, an unbound Roadie catalog and temporary receipt
storage. Cases cover callback values, records, membership, comparisons,
arithmetic, syntax failures, unsupported async execution, and output retained
before failure. They assert receipt completion/failure, captured output, no
requested provider connection, and successful receipt verification.

Without `ROAD_TEST_ROADOS`, these tests skip explicitly. They do not establish
live device dispatch or broker delivery. Offline NATS launcher checks use the
separate `ROAD_TEST_BUS_ROOT` setting documented in `NATS.md`.

The error-class label (for example `KeyError`, `NameError`, or
`ZeroDivisionError`) preserves useful failure information in RoadOS receipts
without restoring tracebacks. It is descriptive diagnostic text, not a new
structured error schema.
