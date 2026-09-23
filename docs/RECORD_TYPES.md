# Road records in the Python interpreter

Records make the existing dictionary-based object model convenient to declare
and construct. They do not introduce Python classes as Road values.

```road
type Device:
    name: string
    online: bool = false
    history: list[any] = []

let lucidia = Device{
    name: "Lucidia",
}
lucidia.history.append("declared")
print(lucidia.name)
```

Run the checked-in example with:

```bash
python3 roadc.py run examples/record_types.road
```

## Construction contract

- Declare a record with an indented list of `name: annotation` fields. A field
  may supply `= expression` as its default. Field names are identifiers.
- Construct with `TypeName{field: expression, ...}`. Constructors may span
  lines and allow a trailing comma. `TypeName{}` works if every field has a
  default. Nested constructors work as expressions, including inside functions.
- Missing required fields and unknown fields fail before any supplied value or
  default expression runs. Duplicate fields in a declaration or constructor are
  syntax errors; a name that does not refer to a record declaration cannot be
  used as a constructor.
- Explicit values run once, left to right, in the caller's environment. Omitted
  defaults then run once in declaration order, in the declaration's lexical
  environment. Provided fields never evaluate their defaults. Earlier field
  values are not introduced as variables for later defaults.
- A default is an expression evaluated at construction time. Literal `[]` and
  `{}` create fresh containers each time. A default referring to an existing
  mutable variable shares that variable's object; it is not copied. Captured
  environments retain live bindings, not snapshots of their values.
- The result is an ordinary dictionary in declaration order, with no injected
  type, identity, permission, or authority metadata. Existing dot access, indexed
  access, mutations, dictionary methods, and external verb functions still work.
  As with existing dictionaries, fields named `keys`, `values`, or `items` are
  accessed by index because those dot names select dictionary methods.
- Constructor bindings can be passed or returned as values and assigned an
  alias: `let Other = Device`, then `Other{name: "Octavia"}`. Repeated local
  declarations capture their own invocation's environment.

Grouping delimiters `()`, `[]`, and `{}` suppress block indentation inside an
expression. Closing a multiline constructor resumes the surrounding block.
Unclosed, mismatched, or unexpected delimiters produce syntax errors with
source locations.

## Implementation limits

Annotations are preserved in the AST but are not checked against values. This
matches existing variable and function annotations; it is not a static type
checker, nominal instance system, or an assignment guard. Records stay mutable
and may gain fields after construction just like other Road dictionaries.

This increment supports declaration and construction in the Python interpreter.
It does not add inheritance, methods inside declarations, field-to-field default
binding, exports, a multiline REPL, or C compiler record support. Defaults are
ordinary Road expressions and can have the same local effects as other
expressions; constructor validation is not a sandbox or transaction.

A record with a Route, permissions, or an `authorized` field is data supplied by
the program. Constructing it does not resolve the Route, verify an identity,
grant authority, invoke a provider, or execute a device operation. Runtime
authorization remains at the RoadOS boundary.

## Continuity

This implements the next step identified by RoadC PR #4's object-model contract.
The object-model foundation and record implementation are integrated with
`main`, including short-circuit evaluation and compound dictionary updates.
Tests execute the checked-in record example as well as the object-model examples.
