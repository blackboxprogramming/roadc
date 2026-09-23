"""Each evaluation of a function declaration captures its own environment."""

from interpreter import Interpreter
from lexer import Lexer
from parser import Parser


def parse(source):
    return Parser(Lexer(source).tokenize()).parse_program()


def run(source):
    runtime = Interpreter()
    runtime.run(parse(source))
    return runtime.global_env


def test_factory_closures_keep_distinct_values_and_defaults():
    env = run('fun make(value):\n'
              '    fun get(extra = value):\n        return value + extra\n'
              '    return get\n'
              'let first = make(2)\nlet second = make(9)\n'
              'let a = first()\nlet b = second()\nlet c = first(3)\n')
    assert [env.get(key) for key in ['a', 'b', 'c']] == [4, 18, 5]


def test_factory_counters_keep_independent_mutable_state():
    env = run('fun make(value):\n'
              '    fun next():\n        value = value + 1\n        return value\n'
              '    return next\n'
              'let first = make(0)\nlet second = make(10)\n'
              'let a = first()\nlet b = second()\nlet c = first()\n')
    assert [env.get(key) for key in ['a', 'b', 'c']] == [1, 11, 2]


def test_reusing_ast_does_not_rebind_another_runtime():
    program = parse('fun get():\n    return value\n')
    first, second = Interpreter(), Interpreter()
    first.global_env.set('value', 1)
    second.global_env.set('value', 2)
    first.run(program)
    second.run(program)
    first.run(parse('let result = get()\n'))
    second.run(parse('let result = get()\n'))
    assert first.global_env.get('result') == 1
    assert second.global_env.get('result') == 2
    assert not hasattr(program.statements[0], '_closure_env')


def test_sibling_closures_share_their_single_factory_environment():
    env = run('fun make():\n    let value = 0\n'
              '    fun add():\n        value = value + 1\n        return value\n'
              '    fun get():\n        return value\n'
              '    return [add, get]\n'
              'let pair = make()\nlet a = pair[0]()\nlet b = pair[1]()\n')
    assert [env.get(key) for key in ['a', 'b']] == [1, 1]
