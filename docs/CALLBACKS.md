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
