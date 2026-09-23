# Logical operators in the Python interpreter

`and` and `or` evaluate left to right and short-circuit:

- `left and right` returns `left` when it is falsey; otherwise it evaluates and returns `right`.
- `left or right` returns `left` when it is truthy; otherwise it evaluates and returns `right`.

The selected operand is returned without conversion to a boolean. The left
operand runs once; the right operand runs at most once. A skipped expression
cannot print, call a function, or raise an evaluation error. A required right
operand still propagates its errors normally.

```road
let denominator = 0
let safe = denominator != 0 and 10 / denominator > 1
let name = "" or "Roadie"
```

This describes the Python tree-walking interpreter only. It does not establish
C compiler parity, static validation, or a permission boundary.
