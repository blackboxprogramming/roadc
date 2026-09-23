# List and vector separators

List elements and vector components require commas between expressions:
`[1, 2]` and `vec2(1, 2)` are valid; `[1 2]` and `vec2(1 2)` raise located
syntax errors. Empty lists and existing trailing-comma syntax remain accepted.

An element can itself contain calls, arithmetic, nested collections, or index
access. For example, `[[8, 9][1]]` is a one-element list containing `9`, not two
adjacent list elements. Normal expression parsing determines these boundaries.

This change concerns separators in the Python parser. It does not add multiline
grouping support or change dictionary, set, tuple, or C compiler syntax.
