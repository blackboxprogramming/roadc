# Loop control in Python RoadC

`break` exits the nearest executing loop in the current function; `continue`
starts its next iteration. Both `for` and `while` handle these statements.

A called function cannot break or continue a caller's loop. If either statement
escapes the function's own loops, calling that function raises `RuntimeError`
with its name and the invalid control statement. This also applies to nested
function definitions: a surrounding function's loop belongs to its caller.

Validation happens when the statement executes, not during parsing. Unexecuted
branches are not checked, and prior side effects are not rolled back. Ordinary
function returns and control statements inside the function's own loops retain
their behavior. This change concerns the Python interpreter only.

At the program boundary, an executed `return` outside a function or `break` /
`continue` outside a loop raises a descriptive `RuntimeError` instead of leaking
the interpreter's internal control-flow signal. This includes statements inside
top-level conditionals. A top-level loop does not make `return` valid. Earlier
effects remain, and the interpreter can run another program after the error.
