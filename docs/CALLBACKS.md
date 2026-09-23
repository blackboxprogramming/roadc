# Collection callbacks

`map` and `filter` accept Road functions and builtins, including aliases, and
return lists in input order:

```road
fun double(value):
    return value * 2
fun positive(value):
    return value > 0
let doubled = map(double, 1..4)
let kept = filter(positive, [-1, 0, 2, 3])
```

The results are `[2, 4, 6]` and `[2, 3]`. `filter` keeps the original input
values whose callback results are truthy. Both functions evaluate eagerly.

`map` accepts one or more iterables and calls its function with one value from
each, stopping at the shortest iterable. `filter` accepts exactly one iterable
and calls its predicate with one value. Defaults and final variadic parameters
use the same rules as ordinary Road calls. Each callback invocation gets a fresh
call scope, with its closure's live bindings.

Builtin argument counts are checked before any arguments run. The callback
expression is then evaluated, and Road/builtin signatures are checked before
input expressions run, even for empty inputs. Inputs evaluate once, left to
right; callbacks then run in iteration order. Bound member values such as `items.append` use the same checks, including
through aliases and with empty callback inputs. They retain the original receiver
if its variable is later rebound. Arbitrary callables supplied by an embedding
host retain host-language argument validation.

Callback failures stop processing; earlier effects are not rolled back. A
callback's `break` or `continue` cannot control a caller's loop. These are local
Python-interpreter operations, not parallel execution or C compiler features.

## Other builtin calls

Ordinary builtin adapters also validate positional argument counts before
evaluating argument expressions. Extra arguments are errors; they are never
silently ignored. Road exposes a subset of Python's builtin signatures:

| Builtins | Accepted argument count |
| --- | --- |
| `print`, `zip` | Zero or more |
| `min`, `max` | One or more |
| `range` | One to three |
| `input`, `list`, `dict`, `set` | Zero or one |
| `round` | One or two |
| Other ordinary builtin adapters | One, except the two-argument `isinstance` adapter |

In particular, optional Python parameters such as the base in `int`, the start
in `sum`/`enumerate`, and keyword options are not exposed by these Road adapters.
The type keywords `int`, `float`, `bool`, `list`, `dict`, and `set` can also be
called as constructors, for example `list(0..3)` or `int("12")`. Their use in
annotations is unchanged. In expression position these constructor keywords
also represent builtin function values. `type Name:` still introduces a record
declaration; `type(value)` and bare `type` in expressions refer to the inspection
builtin. Argument value validation happens after evaluation, and short-circuit
guards still skip calls.

## Builtin values and aliases

```road
let transform = map
let numbers = transform(int, ["0", "3", "7"])
let positive = filter(bool, numbers)
let labels = map(str, positive)
```

Builtin values can be stored in collections, passed to Road functions, returned,
or used as default parameters. Aliases retain the builtin's argument checks;
aliasing `map` or `filter` also preserves callback validation before input
expressions run. Invalid callback arity is rejected even for empty inputs.
`map(map, [str, abs], [[1, 2], [-3, 4]])` produces
`[["1", "2"], [3, 4]]`. Nested collection calls receive values already evaluated
by their outer call; they cannot undo those earlier effects.

Name lookup is now consistent between direct calls and function values: an
ordinary local declaration or parameter such as `len` or `map` shadows that
builtin. Previously direct calls bypassed such bindings. Save an alias before
shadowing if the original builtin is needed. Constructor type keywords remain
reserved in declaration/parameter names. Each interpreter owns its bindings.

The basic constructor values also serve as descriptors for `isinstance`.
See [value inspection](TYPE_INSPECTION.md) for supported types and record limits.
Existing adapter signatures above, eager evaluation, and the C compiler's
separate feature set are unchanged.

Run `python3 roadc.py run examples/builtin_callbacks.road` for a local example.
With a trusted sibling RoadOS checkout, verify success/failure receipts too:

```bash
ROAD_TEST_ROADOS="$PWD/../RoadOS" python3 -m pytest tests/test_builtin_workspace.py -q
```

The integration check launches the selected RoadOS code and this interpreter;
it uses temporary projects and does not connect to a provider.

## Bound member signatures

| Methods | Accepted argument count |
| --- | --- |
| Dictionary `keys`, `values`, `items`; list `pop`; string `upper`, `lower`, `strip` | Zero |
| List `append`; string `startswith`, `endswith`, `contains` | One |
| String `split` | Zero or one |
| String `replace` | Two |

Arity is checked before argument expressions run. Value errors, such as popping
an empty list, occur when the validated call executes. `split()` keeps its
existing literal-space separator. List/string `length` remains a value, and
dictionary method names retain precedence over same-named keys in dot access.
