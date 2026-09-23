# Arithmetic precedence

Exponentiation is right-associative and binds more tightly than a unary sign
on its base. Its exponent may itself be signed:

| Expression | Result |
| --- | --- |
| `-2 ** 2` | `-4` |
| `(-2) ** 2` | `4` |
| `2 ** -2` | `0.25` |
| `2 ** 3 ** 2` | `512` |
| `(2 ** 3) ** 2` | `64` |
| `~2 ** 3` | `-9` |

Unary `+`, `-`, and `~` bind above multiplication/division/remainder and below
a power on their right. Parentheses override grouping. Calls and indexing bind
above exponentiation. Operand expressions still run once, from left to right;
right-associativity determines grouping, not evaluation order.

Earlier Python-interpreter versions grouped `-2 ** 2` as `(-2) ** 2`; use those
parentheses explicitly if that behavior is intended. This change does not alter
the separate C compiler.
