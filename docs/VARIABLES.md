# Variable bindings

`let` and `var` introduce assignable bindings. `const` introduces a binding
that cannot be rebound with plain assignment, compound assignment, or a `for`
loop in the same scope:

```road
let retries = 0
var status = "starting"
const limits = [3, 5]
retries += 1
status = "ready"
limits.append(7) # the binding is fixed; the list remains mutable
```

Assigning to a constant raises `TypeError` when that assignment executes. A
function that closes over a constant cannot reassign it either. A function may
create a local binding with the same name; that local shadows the outer one.
`const` controls rebinding only: it does not freeze lists, dictionaries, or
other values, and it does not enforce type annotations.

A constant declaration may omit its initializer, in which case its value is
`None` and it remains immutable. Redeclaring a constant in the same scope is an
error. Syntax checking verifies that the declaration parses but does not
execute assignments, so reassignment failures are runtime errors.

These semantics apply to the Python interpreter; they do not claim C compiler
parity. See [syntax checking](CHECK.md) for the `check` command.
