# Road — RoadC implementation

<!-- BLACKROAD:CANON:START -->
## The Road. Pave Tomorrow.

**We access it all at RoadOS.**  
**We collaborate with Roadies.**  
**We code in Road.**

*Integration is Innovation.*

Pick up your Roadies. Discover the BlackRoad together.

[Product names, brand language, and implementation boundaries](BLACKROAD_CANON.md)
<!-- BLACKROAD:CANON:END -->

> A Road language implementation with Python-style indentation, built from scratch — a tree-walking interpreter in Python and a zero-dependency C99 compiler.


[![CI](https://github.com/blackboxprogramming/roadc/actions/workflows/ci.yml/badge.svg)](https://github.com/blackboxprogramming/roadc/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB.svg)](https://python.org)
[![C99](https://img.shields.io/badge/C99-zero_deps-A8B9CC.svg)](https://en.wikipedia.org/wiki/C99)
[![License](https://img.shields.io/badge/license-Proprietary-9c27b0)](LICENSE)

## What Works Today

The Python interpreter supports:

- **Variables**: `let`, `var`, `const` with optional type annotations
- **Functions**: `fun` keyword, parameters, `return`, recursion, closures
- **Control flow**: `if`/`elif`/`else`, `while`, `for`/`in`, `break`, `continue`
- **Types**: integers, floats, strings (with `{var}` interpolation), booleans, colors (`#FF1D6C`)
- **Collections**: lists, dicts, sets, tuples, ranges
- **Operators**: arithmetic, comparison, logical, bitwise, compound assignment
- **Builtins**: `print`, `len`, `range`, `str`, `int`, `abs`, `min`, `max`, `sorted`, `input`, and more
- **Member access**: string/list/dict methods (`.upper()`, `.append()`, `.keys()`)
- **Callbacks**: `map` and `filter` invoke Road functions and closures over local collections. [Callback semantics](docs/CALLBACKS.md).
- **Records**: `type Device:` declarations and `Device{name: "Lucidia"}` construction, with required fields and per-construction defaults; values remain ordinary dictionaries. [Record semantics and limits](docs/RECORD_TYPES.md).

```road
fun fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

let result = fibonacci(10)
print(result)  # 55
```

```road
let name = "world"
let msg = "hello {name}"
print(msg)  # hello world

let xs = [1, 2, 3, 4, 5]
let total = 0
for x in xs:
    total += x
print(total)  # 15
```

## Architecture

```
source.road
    |
    v
  Lexer (lexer.py, 462 LOC)
    |  Tokens: keywords, literals, operators, INDENT/DEDENT
    v
  Parser (parser.py, 826 LOC)
    |  AST nodes defined in ast_nodes.py (462 LOC)
    v
  Interpreter (interpreter.py, 320 LOC)
       Tree-walking execution with Environment chain
```

The C compiler (`roadc.c`, 618 LOC) is a separate implementation that compiles `.road` files to native executables. Zero external dependencies — just a C99 compiler.

```bash
gcc -std=c99 -O2 -o roadc roadc.c
./roadc program.road
```

## Development

```bash
# Run a .road file
python3 roadc.py run examples/demo.road

# Check syntax without executing the program
python3 roadc.py --check examples/demo.road

# Check multiple files and emit a machine-readable report
python3 roadc.py check first.road second.road --json

# Run tests (30+ tests)
pytest tests/ -v

# Build C compiler
gcc -std=c99 -O2 -o roadc roadc.c

# Start REPL
python3 roadc.py repl
```

### Syntax checking

`check` and `--check` run the Python lexer and parser on UTF-8 files. They never
execute source, construct an interpreter, prompt for input, or evaluate function
calls. A successful check means the current parser accepts the syntax; it does
not validate names, types, runtime behavior, or compatibility with the separate
C compiler. Statements whose parser implementation is unfinished produce an
error instead of hanging. The first diagnostic per file is reported, and checking
continues with the remaining files in argument order.

Text output sends successful results to stdout and errors to stderr. `--json`
sends one JSON document to stdout, with no other output for source/read errors:

```json
{"schema_version": 1, "command": "check", "ok": true, "files": [{"path": "program.road", "ok": true, "diagnostics": []}]}
```

Each diagnostic has `code`, `stage`, `severity` (`error`), `message`, `line`, and
`column`. Stages are `read`, `lex`, or `parse`; codes are `io_error`,
`encoding_error`, `syntax_error`, or `nesting_limit`. Locations are one-based when
the lexer/parser supplies them and `null` otherwise. The JSON structure and codes
are the automation contract; message wording is informational and may change.
Paths retain the spelling passed on the command line.

Exit codes: **0** means all files passed, **1** means a file failed to read or
parse, and **2** means invalid check-command arguments. Usage errors remain text
on stderr even with `--json`. Use `--` before a filename beginning with `-`.

## Roadmap

- [ ] Type checker (static analysis pass between parser and interpreter)
- [ ] Bytecode VM (replace tree-walking for performance)
- [ ] Standard library (file I/O, math, networking)
- [ ] 3D scene graph (`space`, `cube`, `sphere` keywords — lexer ready, runtime not yet)
- [ ] Package manager
- [ ] Self-hosting compiler

## License

Proprietary — BlackRoad OS, Inc.

## Related Projects

| Project | Description |
|---------|-------------|
| [RoadC Playground](https://github.com/blackboxprogramming/roadc-playground) | Interactive browser IDE for RoadC |
| [Universal Computer](https://github.com/blackboxprogramming/universal-computer) | Turing machine simulator |
| [Quantum Math Lab](https://github.com/blackboxprogramming/quantum-math-lab) | Mathematical computation toolkit |

---

## About BlackRoad

**BlackRoad** is the ecosystem. **RoadOS** is the portable computer and control environment where people access their work and Roadies can operate visibly within authorized boundaries. **Roadies** are AI collaborators; **Roadie** is the coordinating meta-AI; **Road** is the language.

RoadC is an implementation of Road. The Python interpreter and C compiler described above are implementation tools, not separate product definitions. Local operation, dependencies, supported syntax, and compatibility must be assessed for each implementation.

**Ramps** are connections to external providers and services. Their use follows explicit permissions and the implementation’s actual data flow. The shared canon makes no blanket claim of zero dependencies, universal hardware support, or connected production infrastructure.

Built by [BlackRoad OS, Inc.](https://github.com/BlackRoad-OS-Inc).

<details>
<summary>The BlackRoad ecosystem</summary>

| Organization | Focus |
|---|---|
| [BlackRoad OS](https://github.com/BlackRoad-OS) | Core platform and applications |
| [BlackRoad OS, Inc.](https://github.com/BlackRoad-OS-Inc) | Corporate and enterprise |
| [BlackRoad AI](https://github.com/BlackRoad-AI) | Artificial intelligence and ML |
| [BlackRoad Hardware](https://github.com/BlackRoad-Hardware) | Edge hardware and IoT |
| [BlackRoad Security](https://github.com/BlackRoad-Security) | Cybersecurity and auditing |
| [BlackRoad Quantum](https://github.com/BlackRoad-Quantum) | Quantum computing research |
| [BlackRoad Agents](https://github.com/BlackRoad-Agents) | Autonomous AI agents |
| [BlackRoad Network](https://github.com/BlackRoad-Network) | Mesh and distributed networking |
| [BlackRoad Education](https://github.com/BlackRoad-Education) | Learning and tutoring platforms |
| [BlackRoad Labs](https://github.com/BlackRoad-Labs) | Research and experiments |
| [BlackRoad Cloud](https://github.com/BlackRoad-Cloud) | Self-hosted cloud infrastructure |
| [BlackRoad Forge](https://github.com/BlackRoad-Forge) | Developer tools and utilities |

</details>

**Links** — [blackroad.io](https://blackroad.io) ·
[docs.blackroad.io](https://docs.blackroad.io) ·
[chat.blackroad.io](https://chat.blackroad.io) ·
[search.blackroad.io](https://search.blackroad.io)

*Remember the Road. Pave Tomorrow.*

## RoadOS source integration

Browse this clone's committed source in RoadOS Code and import selected files with commit/blob provenance. [Setup and language compatibility](docs/ROADOS_INTEGRATION.md).

## Offline ecosystem check

This repository declares its integration role and required files in
[`ecosystem.json`](ecosystem.json). With `road`, `RoadOS`, `roadies`, `roadc`,
`roadie`, and `BlackRoadOS-RoadOS` as sibling checkouts, run from their parent:

```bash
python3 RoadOS/ecosystem.py --root .
```

The checker reports all six components, hashes required files, and checks that
their canon copies agree. It does not execute repository code, load models,
connect providers, or establish deployment readiness. See the
[ecosystem contract](https://github.com/blackboxprogramming/RoadOS/blob/main/ECOSYSTEM.md).

### Compare local observations

From the parent of the six sibling checkouts:

```bash
python3 RoadOS/ecosystem.py --root . --save baseline.json
python3 RoadOS/ecosystem.py --root . --baseline baseline.json --save current.json
```

Snapshots preserve file hashes and canon agreement across Road, RoadOS, and
Roadies. The comparison identifies changed, newly observed, or no longer observed
files. Existing snapshot files are never overwritten. These checks do not run
repository code or connect providers. See [comparison behavior and exit codes](https://github.com/blackboxprogramming/RoadOS/blob/main/ECOSYSTEM.md#save-and-compare-observations).

## NATS messaging

This component has an opt-in NATS JetStream adapter for durable, content-hashed
artifact notifications. See [NATS setup and commands](NATS.md). Local receipts
and execution permissions remain authoritative.
