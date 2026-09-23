# Range expressions

The Python interpreter supports `start..stop` as a lazy sequence of integers.
It includes `start` and excludes `stop`, increasing by one. Equal or descending
bounds produce an empty range.

```road
for i in 0..3:
    print(i)
```

This prints `0`, `1`, and `2`, each on its own line. Try the runnable example:

```sh
python3 roadc.py run examples/ranges.road
```

Bounds can be integer literals, variables, function calls, or arithmetic:

```road
let start = -2
let stop = 3
let values = start..stop
let middle = (1 + 1)..(2 * 3)
let second = values[1]
```

Bounds are evaluated once, from left to right. Arithmetic binds more tightly
than `..`, and comparisons bind less tightly. For example, `1 + 1..2 * 3`
means `(1 + 1)..(2 * 3)`. Parenthesize a range before indexing it directly:
`(2..5)[1]` is `3`.

Both bounds must be integers; floats, strings, and booleans produce a type
error at the range operator's line and column. Range construction does not
allocate a list, but iterating a large range still takes time.

Chained ranges (`0..2..4`), inclusive `...` ranges, and omitted bounds are not
supported. This does not implement list slicing with ranges, match patterns,
or support in the separate C compiler.
