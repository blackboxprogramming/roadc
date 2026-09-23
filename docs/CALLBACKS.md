# Collection callbacks

`map` and `filter` accept Road functions, including closures and aliases, and
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
expression is then evaluated, and Road function signatures are checked before
input expressions run, even for empty inputs. Inputs evaluate once, left to
right; callbacks then run in iteration order. Existing callable member values
such as `items.append` also work, with their host-language argument validation.

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
annotations is unchanged. This does not add first-class builtin names or make
bare type keywords into values; the `type` declaration keyword remains reserved.
Argument value
validation happens after evaluation, and short-circuit guards still skip calls.
