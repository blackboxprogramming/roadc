<!-- BlackRoad SEO Enhanced -->

# roadc

> Part of **[BlackRoad OS](https://blackroad.io)** — Sovereign Computing for Everyone

[![BlackRoad OS](https://img.shields.io/badge/BlackRoad-OS-ff1d6c?style=for-the-badge)](https://blackroad.io)
[![blackboxprogramming](https://img.shields.io/badge/Org-blackboxprogramming-2979ff?style=for-the-badge)](https://github.com/blackboxprogramming)
[![License](https://img.shields.io/badge/License-Proprietary-f5a623?style=for-the-badge)](LICENSE)

**roadc** is part of the **BlackRoad OS** ecosystem — a sovereign, distributed operating system built on edge computing, local AI, and mesh networking by **BlackRoad OS, Inc.**

## About BlackRoad OS

BlackRoad OS is a sovereign computing platform that runs AI locally on your own hardware. No cloud dependencies. No API keys. No surveillance. Built by [BlackRoad OS, Inc.](https://github.com/BlackRoad-OS-Inc), a Delaware C-Corp founded in 2025.

### Key Features
- **Local AI** — Run LLMs on Raspberry Pi, Hailo-8, and commodity hardware
- **Mesh Networking** — WireGuard VPN, NATS pub/sub, peer-to-peer communication
- **Edge Computing** — 52 TOPS of AI acceleration across a Pi fleet
- **Self-Hosted Everything** — Git, DNS, storage, CI/CD, chat — all sovereign
- **Zero Cloud Dependencies** — Your data stays on your hardware

### The BlackRoad Ecosystem
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

### Links
- **Website**: [blackroad.io](https://blackroad.io)
- **Documentation**: [docs.blackroad.io](https://docs.blackroad.io)
- **Chat**: [chat.blackroad.io](https://chat.blackroad.io)
- **Search**: [search.blackroad.io](https://search.blackroad.io)

---


[![CI](https://github.com/blackboxprogramming/roadc/actions/workflows/ci.yml/badge.svg)](https://github.com/blackboxprogramming/roadc/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB.svg)](https://python.org)
[![C99](https://img.shields.io/badge/C99-zero_deps-A8B9CC.svg)](https://en.wikipedia.org/wiki/C99)
[![License](https://img.shields.io/badge/license-Proprietary-9c27b0)](LICENSE)

A programming language with Python-style indentation, built from scratch. Two implementations: a tree-walking interpreter in Python, and a zero-dependency C99 compiler.

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
python roadc.py examples/fibonacci.road

# Run tests (30+ tests)
pytest tests/ -v

# Build C compiler
gcc -std=c99 -O2 -o roadc roadc.c

# Start REPL
python roadc.py
```

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
