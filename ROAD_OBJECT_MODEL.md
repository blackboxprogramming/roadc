# Road Object Model

Road does not need to inherit Python's object model just because the current tree-walking interpreter is implemented in Python.

The runtime already gives Road enough primitives to express useful objects directly:

- **dict**: named state
- **list**: ordered changing history or membership
- **set**: unique capabilities and permissions
- **tuple**: fixed identity-shaped values
- **fun**: behavior
- **functions as values**: routing and dispatch

That means a useful Road object can be represented today as explicit data plus verbs.

```road
fun make_device(name, kind, permissions):
    return {"name": name, "kind": kind, "online": false, "permissions": permissions, "identity": (name, kind), "history": []}

let lucidia = make_device("Lucidia", "Raspberry Pi", {"start", "stop", "status"})
```

Member access already makes the record readable:

```road
print(lucidia.name)
print(lucidia.identity)
```

Mutation is equally explicit:

```road
lucidia.online = true
lucidia.history.append({"action": "start"})
```

## Behavior as verbs

Behavior does not need to be hidden inside an object. Road can keep actions visible and English-first:

```road
fun start(device):
    device.online = true
    return "started"
```

Functions are values in the interpreter, so dispatch tables work without a class system:

```road
let actions = {"start": start, "stop": stop, "status": status}

fun dispatch(action, device):
    let handler = actions[action]
    return handler(device)
```

The result is a small object model with inspectable state and inspectable behavior rather than implicit Python machinery.

## Mapping the familiar concepts

| Familiar concept | Road runtime representation |
|---|---|
| object fields | dict entries |
| mutable history | list |
| capabilities / permissions | set |
| stable identity tuple | tuple |
| methods | verb functions |
| method table | dict of functions |
| invocation | function call through the table |

## `type` is the next compiler/runtime layer

The repository already contains `TypeDefinition` and `TypeField` AST nodes, and the Quickstart documents syntax such as:

```road
type User:
    name: string
    age: int
```

The parser's `parse_type_definition` path is still a stub, so that syntax is not yet part of the working interpreter path. The next core step is to make `type` lower into the same explicit runtime model described above rather than inventing a second incompatible object system.

A future constructor can therefore be syntactic sugar:

```road
type Device:
    name: string
    kind: string
    online: bool = false

let lucidia = Device{
    name: "Lucidia",
    kind: "Raspberry Pi"
}
```

Conceptually lowering to:

```road
let lucidia = {"name": "Lucidia", "kind": "Raspberry Pi", "online": false}
```

That keeps Road sovereign at the language level while Python remains only one implementation substrate.

## Working example

See [`examples/road_objects.road`](examples/road_objects.road).

The accompanying tests lock down object composition, function dispatch, permissions-as-data, and receipt-style history behavior in the current interpreter.
