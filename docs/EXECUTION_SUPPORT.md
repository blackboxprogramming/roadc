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

RoadOS uses the process exit code to classify a run receipt. This failure
behavior prevents an ignored import or export from appearing as a completed
workspace run. Run the companion check in the RoadOS repository:

```bash
ROAD_TEST_ROADC="$PWD/../roadc" python3 -m unittest discover \
  -s tests -p test_roadc_execution_integration.py -v
```

Only opt in with a trusted checkout: RoadOS runs the selected runtime's code.
These checks cover the Python implementation, not C compiler parity.
