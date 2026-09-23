# Vector constructors in Python RoadC

`vec2`, `vec3`, and `vec4` require exactly two, three, and four components,
respectively. A mismatched count raises a located `TypeError` before any
component expression runs. Shape checking happens at evaluation time, so a
short-circuited expression does not construct or validate its vector.

For a valid count, components evaluate once from left to right and the result
is a tuple. Component evaluation errors propagate normally; earlier effects
are not rolled back. Component types are not constrained to numbers, and this
does not add vector arithmetic, broadcasting, or C compiler support.
