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
