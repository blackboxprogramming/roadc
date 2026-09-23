# Compound assignment in Python RoadC

`+=`, `-=`, `*=`, and `/=` support variables, list/dictionary indices, and
dictionary members such as `device.count += 1`.

The target object and index evaluate once, in that order. Its existing value
is read before the right-hand expression evaluates. The arithmetic result is
then assigned to the original target. A missing entry or invalid target raises
an error instead of silently discarding the update; target lookup failures
happen before the right-hand expression runs.

These operators use ordinary arithmetic followed by assignment, not Python's
in-place operators. Prior side effects are not rolled back if arithmetic or
the final write fails (for example, writing to an immutable tuple). Plain `=`
assignment and the C compiler are unchanged.
