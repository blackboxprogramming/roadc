"""`const` prevents rebinding while retaining ordinary value semantics."""
import pytest

from interpreter import Interpreter
from parser import parse


def run(source):
    runtime = Interpreter()
    runtime.run(parse(source))
    return runtime


@pytest.mark.parametrize('assignment', ['answer = 42', 'answer += 1'])
def test_constant_assignment_is_rejected(assignment):
    with pytest.raises(TypeError, match="Cannot reassign constant 'answer'"):
        run('const answer = 41\n' + assignment + '\n')


def test_constant_assignment_inside_closure_is_rejected():
    with pytest.raises(TypeError, match="Cannot reassign constant 'answer'"):
        run('''const answer = 41
fun change():
    answer = 42
change()
''')


def test_loop_cannot_rebind_same_scope_constant():
    with pytest.raises(TypeError, match="Cannot reassign constant 'item'"):
        run('''const item = 0
for item in [1]:
    print(item)
''')


def test_constants_allow_mutable_values_and_local_shadowing():
    runtime = run('''const values = [1]
values.append(2)
fun update():
    let values = [8]
    values.append(9)
    return values
let local = update()
let captured = values[1]
''')
    env = runtime.global_env
    assert env.get('values') == [1, 2]
    assert env.get('local') == [8, 9]
    assert env.get('captured') == 2


def test_mutable_declarations_remain_assignable():
    runtime = run('''let a = 1
var b = 2
a = 3
b += 2
''')
    assert runtime.global_env.get('a') == 3
    assert runtime.global_env.get('b') == 4
