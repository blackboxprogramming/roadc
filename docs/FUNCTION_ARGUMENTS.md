# Function arguments in the Python interpreter

User-defined functions accept positional arguments, trailing defaults, and an
optional final variadic parameter:

```road
fun collect(first, label = "Road", ...rest):
    return [first, label, rest]
let result = collect(1, "Roadie", 2, 3)
```

Calls validate the signature and argument count before evaluating argument
expressions or running the body. Too few or too many arguments raise TypeError;
missing parameters never silently resolve to same-named outer variables.
Duplicate parameter names, required parameters after defaults, and variadic
parameters that have defaults or are not last also raise TypeError at call time.

Accepted explicit arguments evaluate once, left to right in the caller's scope.
Omitted defaults then evaluate in parameter order in the new call environment:
earlier parameters are available and outer names use the defining closure.
Supplied values skip their defaults. Mutable literal defaults are constructed
per call; defaults referencing an existing mutable value retain that sharing.
The final variadic parameter receives a list, including an empty list when no
arguments remain. Errors in required argument/default expressions propagate.

Validation happens at call time, not declaration time. The callee expression
itself is resolved first. This is not a sandbox or transaction: side effects
from accepted argument expressions are not rolled back if a later one fails.
Built-ins, member methods, type annotations, and the C compiler are unchanged.
