# RoadC syntax check

```sh
python3 roadc.py check examples/demo.road
python3 roadc.py --check examples/record_types.road examples/road_objects.road --json
```

`check` tokenizes and parses UTF-8 files without executing their statements or
record defaults. It checks every supplied file in order, including after an
earlier file fails. The exit code is 0 when all files pass, 1 for source/read
errors, and 2 for invalid command arguments.

Text output sends successful results to stdout and diagnostics to stderr.
`--json` emits one structured report on stdout; the schema is documented in the
README. Use `--` before a filename that starts with a dash.

Records are supported. Unfinished `match` and `spawn` statement parsers produce
an error instead of hanging, including inside functions and exports. Checking
does not establish runtime support, type correctness, or C compiler parity.
For example, an export can pass syntax checking even though the Python runtime
does not execute exports. The same parser rejects unfinished `match` and `spawn`
syntax in `run`, `parse`, the REPL, and the public Python parsing API.

This consolidates the overlapping work in PRs #8 and #9 into the batch-capable
interface from #8.
