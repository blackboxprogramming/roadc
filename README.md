# 🛣️ BlackRoad OS Language

**A revolutionary programming language designed by machines for machines**

## 🌌 What is it?

BlackRoad is a **3D-native**, **type-safe**, **multi-paradigm** programming language that combines:
- The **simplicity** of Python
- The **safety** of Rust
- The **performance** of C++
- The **concurrency** of Go
- The **3D power** of Unity/THREE.js

**Most importantly**: It's designed to run on **Raspberry Pi** with **zero dependencies!**

## 🚀 Quick Start

### Compile the Compiler (C99, zero deps!)
```bash
gcc -std=c99 -O2 -o roadc roadc.c
```

### Run a .road file
```bash
./roadc your_program.road
```

### Start the REPL
```bash
./roadc
```

## 📝 Example Programs

### Hello World
```road
# hello.road
fun main():
    print("Hello, BlackRoad! 🖤🛣️")
```

### Variables & Types
```road
# variables.road
let x: int = 42
let name = "Alexa"
let pi = 3.14159
let active = true
let color = #FF1D6C  # BlackRoad Hot Pink!

var counter: int = 0
counter = counter + 1

const MAX_SPEED: int = 300
```

### Functions
```road
# functions.road
fun greet(name: string) -> string:
    return "Hello, {name}!"

fun add(a: int, b: int) -> int:
    return a + b

fun fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

fun main():
    let result = add(10, 32)
    print(result)  # 42
```

### 3D Scene (The Revolutionary Part!)
```road
# 3d_scene.road
space GameWorld:
    cube Player:
        position: vec3(0, 0, 0)
        rotation: vec3(0, 45, 0)
        scale: vec3(1, 1, 1)
        color: #FF1D6C  # Hot Pink

    sphere Ball:
        position: vec3(2, 1, 0)
        radius: 0.5
        color: #F5A623  # Amber

    light Sun:
        type: directional
        position: vec3(5, 10, 5)
        intensity: 1.0

    camera MainCam:
        position: vec3(0, 2, 5)
        lookAt: vec3(0, 0, 0)
        fov: 75

fun main():
    render(GameWorld, camera: MainCam)
```

### Simple Game
```road
# game.road
type Player:
    name: string
    health: int
    x: float
    y: float

fun create_player(name: string) -> Player:
    return Player{
        name: name,
        health: 100,
        x: 0.0,
        y: 0.0
    }

fun move_player(player: &mut Player, dx: float, dy: float):
    player.x = player.x + dx
    player.y = player.y + dy

fun main():
    var player = create_player("Alexa")

    move_player(&mut player, 5.0, 3.0)

    print("Player {player.name} at ({player.x}, {player.y})")
```

### Async/Concurrency
```road
# async.road
async fun fetchData(url: string) -> string:
    let response = await http.get(url)
    return response.text()

fun main():
    let data = await fetchData("https://api.blackroad.io/status")
    print(data)
```

## 🎯 Language Features

### ✅ Implemented (v0.1)
- [x] Lexer/Tokenizer (Python + C)
- [x] Parser & AST Generator (Python)
- [x] Native C compiler (zero dependencies!)
- [x] Basic syntax highlighting
- [x] REPL support
- [x] Variables (let/var/const)
- [x] Functions
- [x] 3D object definitions
- [x] Type annotations

### 🚧 In Progress
- [ ] Bytecode VM/Interpreter
- [ ] Type checker
- [ ] Memory safety (ownership/borrowing)
- [ ] Standard library
- [ ] 3D rendering engine
- [ ] Package manager

### 🔮 Planned
- [ ] JIT compilation
- [ ] WebAssembly target
- [ ] GPU compute support
- [ ] Neural network primitives
- [ ] Self-hosting compiler

## 🏗️ Architecture

```
┌─────────────────┐
│  Source (.road) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Lexer       │  ← Converts source to tokens
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Parser      │  ← Builds Abstract Syntax Tree
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Type Checker    │  ← Validates types & semantics
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Code Generator  │  ← Bytecode/LLVM IR/Native
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Runtime/VM     │  ← Executes program
└─────────────────┘
```

## 🎨 Design Philosophy

> **"Code should be a conversation between humans and machines, not a monologue."**

### Core Principles
1. **Machine-First**: Designed for AI to parse, generate, and understand
2. **Radical Simplicity**: If it's not essential, it doesn't exist
3. **3D Native**: First-class support for spatial programming
4. **Type-Safe**: Catch errors before runtime
5. **Zero Ambiguity**: One obvious way to do things

### Why Another Language?

Most languages are designed **by humans for humans**. BlackRoad is designed **by machines for machines** (with humans as first-class citizens too!).

- **Python**: Beautiful, but slow and not type-safe
- **Rust**: Safe, but complex syntax
- **C++**: Powerful, but dangerous
- **Go**: Fast, but limited expressiveness
- **JavaScript**: Ubiquitous, but chaotic

**BlackRoad**: All the good parts, none of the bad.

## 📊 Performance Targets

- **Startup time**: < 1ms (C/Rust level)
- **Memory footprint**: < 5MB base runtime
- **Compilation**: < 100ms for 10,000 lines
- **Execution**: Within 2x of C for most workloads
- **3D rendering**: 60 FPS minimum on Raspberry Pi 4

## 🔧 Building from Source

### Requirements
- **Minimal**: Just a C99 compiler (gcc, clang)
- **Optional**: Python 3.x for prototyping tools

### Build Steps
```bash
# Clone the repo
git clone https://github.com/BlackRoad-OS/blackroad-language
cd blackroad-language

# Build native compiler
gcc -std=c99 -O2 -o roadc roadc.c

# Test it
./roadc test.road

# Install (optional)
sudo cp roadc /usr/local/bin/
```

## 🌐 Raspberry Pi Deployment

```bash
# On your Pi
sudo apt update
sudo apt install gcc make

# Build BlackRoad compiler
gcc -std=c99 -O2 -o roadc roadc.c

# Run a 3D scene
./roadc examples/3d_cube.road
```

## 📚 Documentation

- [Language Specification](BLACKROAD_LANGUAGE_SPECIFICATION.md) - Complete language reference
- [Standard Library](docs/stdlib.md) - Built-in functions and modules
- [3D Programming Guide](docs/3d.md) - Creating 3D scenes and games
- [Type System](docs/types.md) - Understanding types and safety
- [Memory Model](docs/memory.md) - Ownership and borrowing

## 🤝 Contributing

BlackRoad is **proprietary** but we welcome feedback!

- **Issues**: File bugs at blackroad.systems@gmail.com
- **Ideas**: Share at amundsonalexa@gmail.com
- **Questions**: Start a discussion

## 📜 License

**Proprietary License - BlackRoad OS, Inc.**

Copyright © 2026 BlackRoad OS, Inc. All rights reserved.

- **Non-commercial use**: Allowed for testing and personal projects
- **Commercial use**: Requires license
- **Redistribution**: Contact us

## 🎯 Roadmap

### v0.1 (Current) - Foundation
- ✅ Lexer & Parser
- ✅ Native C compiler
- ✅ Basic REPL
- ⏳ Bytecode VM

### v0.2 - Execution
- ⏳ Full interpreter
- ⏳ Type checker
- ⏳ Standard library (core)
- ⏳ Error messages

### v0.3 - 3D Power
- ⏳ 3D rendering engine
- ⏳ Physics integration
- ⏳ WebGL/OpenGL backend
- ⏳ Examples & demos

### v0.4 - Performance
- ⏳ JIT compilation
- ⏳ LLVM backend
- ⏳ Optimizations
- ⏳ Benchmarks

### v1.0 - Production Ready
- ⏳ Complete standard library
- ⏳ Package manager (roadpkg)
- ⏳ LSP (IDE support)
- ⏳ Documentation site
- ⏳ Self-hosting compiler

## 💡 Philosophy

### The Golden Ratio
BlackRoad follows the **Golden Ratio (φ = 1.618)** in design:
- Spacing: 8px, 13px, 21px, 34px, 55px, 89px
- Code structure: 38.2% / 61.8% splits
- Performance: Balance simplicity vs power

### Machine-Readable
Every construct is designed to be:
1. **Parseable** by regex/simple tools
2. **Analyzable** by AI
3. **Transformable** automatically
4. **Verifiable** formally

### Example: Variable Declaration
```road
let x: int = 42
#   ^  ^    ^
#   |  |    └─ Value (optional)
#   |  └────── Type (optional but encouraged)
#   └───────── Name (required)
```

Pattern: `let IDENT [: TYPE] [= EXPR]`

## 🖤 BlackRoad Design System

All BlackRoad projects use the official color palette:

- **Hot Pink**: `#FF1D6C` - Primary accent
- **Amber**: `#F5A623` - Secondary accent
- **Electric Blue**: `#2979FF` - Tertiary accent
- **Violet**: `#9C27B0` - Quaternary accent
- **Background**: `#000000` - Black
- **Text**: `#FFFFFF` - White

Gradients: `135deg, 38.2% & 61.8%` (Golden Ratio)

## 🌟 Made with Love

Created by **Alexa Amundson** for **BlackRoad OS**

> "Building the future, one line of code at a time" 🖤🛣️

---

**BlackRoad OS Language** - Where code meets the 3rd dimension.
