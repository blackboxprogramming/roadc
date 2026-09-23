# Assignment targets in Python RoadC

Plain and compound assignments accept variable names, index access, and member
access. Literal values, arithmetic expressions, and bare function calls cannot
be destinations; the parser rejects them with a located `SyntaxError`.
Access through a call, such as `get_items()[0] = 9`, remains valid syntax.

At runtime, member assignment requires a dictionary. Assigning to a member of
a number, list, or string raises `TypeError` rather than silently doing nothing.
Plain member assignment may create a new dictionary field. Index assignment
uses the target collection's normal key/index and mutability checks.

Plain `=` keeps its existing evaluation order: right-hand expression first,
then target object and index. Compound assignment reads the target first, as
documented in COMPOUND_ASSIGNMENT.md. Runtime failures do not roll back earlier
effects. This is Python interpreter behavior, not C compiler parity.
