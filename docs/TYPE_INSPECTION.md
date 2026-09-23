# Inspecting local values

`type(value)` returns the Python runtime's existing type-name string, such as
`"int"`, `"float"`, `"bool"`, `"str"`, `"list"`, `"dict"`, `"set"`, `"tuple"`, or
`"range"`. `type` can be passed as a callback or saved as an alias:

```road
let inspect_value = type
let kinds = map(inspect_value, [1, "two", true])
# kinds is ["int", "str", "bool"]
```

`type Task:` remains a record declaration. The parser distinguishes it by the
following name; expression uses of `type` reach the inspection builtin.

`isinstance(value, descriptor)` accepts the builtin constructor values `int`,
`float`, `bool`, `str`, `list`, `dict`, and `set`, or a tuple of those descriptors.
Nested tuples work; an empty tuple matches nothing. Aliases keep their meaning:

```road
let numeric_types = (int, float)
fun numeric(value):
    return isinstance(value, numeric_types)
let numbers = filter(numeric, [1, "two", 3.5])
# numbers is [1, 3.5]
```

Checks use the existing host value relationships: `isinstance(true, int)` is
true because this runtime represents booleans using Python's integer subtype;
`isinstance(1, bool)` is false. No conversion is performed. These checks do not
enforce annotations or change how values are stored.

All descriptor entries are validated before matching. `(int, 7)` raises an error
even when the value matches `int`; strings such as `"int"`, lists of descriptors,
ordinary functions, and non-constructor builtins are invalid. Argument expressions
have already been evaluated at that point; their effects are not rolled back.
Ordinary arity checks still precede argument evaluation. Host embedding code may
continue to supply actual Python type objects explicitly.

Records remain plain dictionaries: `type(Task{})` returns `"dict"`, and
`isinstance(Task{}, dict)` is true. A record declaration such as `Task` is not a
nominal type descriptor, so `isinstance(Task{}, Task)` is rejected. Tuple/range
names can be reported by `type`, but those constructor descriptors are not added
here. This is local Python-interpreter behavior; C compiler parity is unchanged.
