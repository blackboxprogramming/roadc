# Interactive Road sessions

Start the Python interpreter with `python3 roadc.py repl`. Variables, functions,
record types, and closures remain available until the session ends.

Single-line input runs immediately. A line whose last meaningful token is `:`
starts a block; enter the body with its normal indentation, then enter a blank
line to submit the entire block:

```text
road> fun double(value):
....>     return value * 2
....>
road> print(map(double, [2, 3]))
[4, 6]
road> exit
```

This supports functions, loops, conditionals (including nested `elif`/`else`),
and record declarations. Trailing header comments are allowed. Colons inside
strings or comments do not start a block. Keep the whole compound statement
together: a blank line submits it rather than separating nested clauses.

The interpreter parses all collected source before executing any of it. A syntax
error rejects that submission and leaves earlier session bindings available.
Runtime errors stop the submission, but effects of statements that already ran
remain; there is no rollback. This is ordinary local code execution, not a
sandbox or a permission boundary.

Ctrl-C cancels unsubmitted input, or interrupts running code, and returns to
`road>`. Interrupting execution also preserves effects already performed.
`exit` and `quit` end the session at the primary prompt. EOF ends the session;
an unsubmitted block is discarded. Those command words inside a collected block
are source text, not session controls.

This adds colon-headed block collection only. It does not add automatic
indentation, multiline bracket/string editing, history storage, expression
echoing, or a change to the separate C interpreter. Use a `.road` file for larger
programs and `python3 roadc.py check FILE` for a syntax-only check.
