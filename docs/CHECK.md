# RoadC syntax check

## Check syntax without execution

```sh
python3 roadc.py check examples/demo.road
```

`check` tokenizes and parses one UTF-8 source file without running its statements.
It exits 0 and prints `Syntax OK` on successful parsing. Invalid syntax, unreadable
files, invalid UTF-8, and parser recursion limits produce an error on stderr and
exit 1. This checks syntax only; it does not prove that the interpreter supports
every parsed feature or that a program will run successfully.

Unfinished statement parsers (`type`, `match`, and `spawn` on this branch)
produce an `Unsupported statement` error, including inside nested blocks or
exports, instead of hanging. Malformed numeric literals produce a clean error
without a Python traceback. The `run` and `parse` commands are unchanged.

PR #8 contains a broader, overlapping checker with batch and JSON output. This
branch retains its single-file interface; reconcile the two before merging
rather than treating them as independent features.
