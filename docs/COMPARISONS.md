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
