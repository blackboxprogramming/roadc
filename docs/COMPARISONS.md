# Chained comparisons

The Python interpreter treats `a < b <= c` as a sequence of pairwise checks,
not as a comparison of an intermediate boolean with `c`.

```road
let inside = 0 <= 5 < 10
let descending = 3 < 2 < 1
```

`inside` is true and `descending` is false. Each reached operand evaluates once,
left to right. Middle values are reused, and the first false comparison skips
all remaining operands. Errors in reached expressions propagate normally.

Chains may mix `==`, `!=`, `<`, `<=`, `>`, and `>=`. They bind below ranges and
bitwise operations, and above logical `not`, `and`, and `or`. Parentheses can
request nested comparison explicitly: `(3 < 2) < 1` compares false to 1 using
the existing runtime semantics and is true.

Single comparisons keep their existing AST representation and behavior.
This corrects the prior left-associative behavior of unparenthesized chains;
code relying on that behavior must add parentheses. C compiler behavior is
unchanged.

## Membership

`in` and `not in` are comparison operators for local collections:

```road
let present = "read" in {"read", "write"}
let absent = 3 not in [1, 2]
let has_name = "name" in {"name": "Lucidia"}
```

All three results are true. Dictionaries test keys, strings test substrings,
and lists, tuples, sets and ranges use their normal Python-interpreter membership
semantics. An incompatible right operand raises a type error.

Membership shares comparison precedence and supports chains: `1 < value in
allowed` checks both pairs and evaluates `value` only once. A false first pair
skips later operands. Logical guards also short-circuit membership expressions.
The contextual `in` marker in `for` loops is unchanged. Membership checks are
local data operations; a permission-like string in a set does not grant runtime
authority.
