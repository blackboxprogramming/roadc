# Bitwise and set operators

The Python interpreter accepts `&`, `^`, `|`, and unary `~` in Road source.
These connect the existing lexer tokens and runtime operations to the parser.

```road
let flags = 4 | 2
let enabled = flags & 2 == 2
let inverted = ~flags
let common = {"read", "write"} & {"read", "status"}
```

The results are `6`, `true`, `-7`, and `{"read"}`. Set operations manipulate
local data; permission-like strings do not grant execution authority.

Precedence, from stronger to weaker, is arithmetic, `&`, `^`, `|`, range `..`,
comparisons, `not`, `and`, then `or`. Unary `~` shares the existing unary `+`/`-`
precedence, below a power on its right (`~2 ** 3` is `-9`). See
[arithmetic precedence](ARITHMETIC.md). Parentheses override grouping.
For example, `1 | 2 & 4` is `1`,
and `1 | 2..4 | 1` constructs the range from `3` up to, but excluding, `5`.

Binary bitwise operators evaluate both operands once, left to right. Logical
`and`/`or` still short-circuit whole expressions. Integer and set operations use
the existing Python runtime semantics, including type errors for incompatible
values. This change does not add shift operators, compound bitwise assignments,
or C compiler parity.
