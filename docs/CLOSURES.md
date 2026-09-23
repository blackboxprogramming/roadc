# Closures in the Python interpreter

Executing a function declaration creates a fresh function value that captures
its defining environment. Calling a factory twice therefore produces closures
over separate calls, including separate captured parameters and local state.
Creating a later closure does not replace an earlier closure's environment.

Sibling functions created in one factory call share that call's environment.
Captured variables remain live: assignment changes the defining environment,
so other closures over that same environment observe the change. This is not
a snapshot or deep copy of captured values.

Parsed function definitions remain reusable syntax. The runtime stores each
capture on a fresh function value while sharing the unmodified syntax for the
body, parameters, and default expressions. Defaults still evaluate at call time
as described in FUNCTION_ARGUMENTS.md. These semantics concern Python RoadC;
they do not establish C compiler parity or isolation of external resources.
