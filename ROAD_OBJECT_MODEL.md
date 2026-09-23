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

## `type` lowers to the same data model

The Python interpreter now parses and runs the Quickstart's record syntax:

```road
type User:
    name: string
    age: int
```

`TypeDefinition` and `TypeField` retain the declaration and annotation metadata.
`RecordLiteral` represents construction; evaluating it produces an ordinary
dictionary, so the existing verbs, member access, indexing, and mutation apply.

A constructor supplies named fields and fills omitted defaults:

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

Construction rejects missing required fields, unknown fields, and duplicate
fields. Defaults run only when omitted, in the declaration's lexical scope;
literal lists and dictionaries are evaluated afresh for each construction.
Annotations remain metadata, matching the existing interpreter: this step does
not add a static checker or enforce types on later field assignments.

See [record semantics and limits](docs/RECORD_TYPES.md) and the executable
[`examples/record_types.road`](examples/record_types.road). The C compiler does
not implement this syntax. Record construction does not dispatch a Route,
authenticate an identity, or grant permissions.

## Working example

See [`examples/road_objects.road`](examples/road_objects.road).

The accompanying tests lock down object composition, function dispatch, permissions-as-data, and receipt-style history behavior in the current interpreter.
