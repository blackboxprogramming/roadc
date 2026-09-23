"""
RoadC Language - Tree-Walking Interpreter
Executes AST nodes produced by the parser
"""

from dataclasses import replace

from ast_nodes import *


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Undefined variable '{name}'")

    def set(self, name, value):
        self.vars[name] = value

    def assign(self, name, value):
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent:
            self.parent.assign(name, value)
            return
        raise NameError(f"Undefined variable '{name}'")


class RecordType:
    """A declaration and its scope; constructed values remain plain dicts."""

    def __init__(self, definition, environment):
        self.definition = definition
        self.environment = environment


class BuiltinFunction:
    """A Road builtin value with the same arity through every call path."""

    def __init__(self, name, implementation, minimum=1, maximum=1):
        self.name = name
        self.implementation = implementation
        self.minimum = minimum
        self.maximum = maximum

    def validate(self, supplied):
        if supplied < self.minimum or (self.maximum is not None and supplied > self.maximum):
            expected = (f'at least {self.minimum}' if self.maximum is None
                        else f'{self.minimum}..{self.maximum}')
            raise TypeError(f'{self.name}: expected {expected} arguments, got {supplied}')

    def __repr__(self):
        return f'<builtin {self.name}>'


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.install_builtins()

    def run(self, program):
        try:
            for stmt in program.statements:
                self.exec_statement(stmt, self.global_env)
        except ReturnSignal:
            raise RuntimeError('return outside a function') from None
        except BreakSignal:
            raise RuntimeError('break outside a loop') from None
        except ContinueSignal:
            raise RuntimeError('continue outside a loop') from None

    def exec_statement(self, stmt, env):
        if isinstance(stmt, VariableDeclaration):
            value = None
            if stmt.initializer:
                value = self.eval_expr(stmt.initializer, env)
            env.set(stmt.name, value)

        elif isinstance(stmt, Assignment):
            value = self.eval_expr(stmt.value, env)
            if isinstance(stmt.target, Identifier):
                env.assign(stmt.target.name, value)
            elif isinstance(stmt.target, IndexAccess):
                obj = self.eval_expr(stmt.target.object, env)
                index = self.eval_expr(stmt.target.index, env)
                obj[index] = value
            elif isinstance(stmt.target, MemberAccess):
                obj = self.eval_expr(stmt.target.object, env)
                if isinstance(obj, dict):
                    obj[stmt.target.member] = value
                else:
                    raise TypeError('Member assignment requires a dictionary')
            else:
                raise TypeError('Invalid assignment target')

        elif isinstance(stmt, CompoundAssignment):
            target = stmt.target
            if isinstance(target, Identifier):
                old = env.get(target.name)
            elif isinstance(target, (IndexAccess, MemberAccess)):
                obj = self.eval_expr(target.object, env)
                if isinstance(target, MemberAccess):
                    if not isinstance(obj, dict):
                        raise TypeError('Compound member assignment requires a dictionary')
                    index = target.member
                else:
                    index = self.eval_expr(target.index, env)
                old = obj[index]
            else:
                raise TypeError('Invalid compound assignment target')
            rhs = self.eval_expr(stmt.value, env)
            ops = {'+=': lambda a, b: a+b, '-=': lambda a, b: a-b,
                   '*=': lambda a, b: a*b, '/=': lambda a, b: a/b}
            value = ops[stmt.operator](old, rhs)
            if isinstance(target, Identifier):
                env.assign(target.name, value)
            else:
                obj[index] = value

        elif isinstance(stmt, ExpressionStatement):
            self.eval_expr(stmt.expression, env)

        elif isinstance(stmt, FunctionDefinition):
            # Each declaration evaluation creates a fresh closure. Keep the
            # parsed definition reusable across factory calls and runtimes.
            function = replace(stmt)
            function._closure_env = env
            env.set(stmt.name, function)

        elif isinstance(stmt, TypeDefinition):
            # Capture each declaration execution separately, including factory calls.
            env.set(stmt.name, RecordType(stmt, env))

        elif isinstance(stmt, ReturnStatement):
            value = self.eval_expr(stmt.value, env) if stmt.value else None
            raise ReturnSignal(value)

        elif isinstance(stmt, BreakStatement):
            raise BreakSignal()

        elif isinstance(stmt, ContinueStatement):
            raise ContinueSignal()

        elif isinstance(stmt, IfStatement):
            self.exec_if(stmt, env)

        elif isinstance(stmt, WhileLoop):
            self.exec_while(stmt, env)

        elif isinstance(stmt, ForLoop):
            self.exec_for(stmt, env)
        else:
            raise RuntimeError(
                f"Unsupported statement: {type(stmt).__name__} at {stmt.line}:{stmt.column}"
            )

    def exec_if(self, stmt, env):
        if self.eval_expr(stmt.condition, env):
            self.exec_block(stmt.then_block, env)
            return
        for condition, block in stmt.elif_blocks:
            if self.eval_expr(condition, env):
                self.exec_block(block, env)
                return
        if stmt.else_block:
            self.exec_block(stmt.else_block, env)

    def exec_while(self, stmt, env):
        while self.eval_expr(stmt.condition, env):
            try:
                self.exec_block(stmt.body, env)
            except BreakSignal:
                break
            except ContinueSignal:
                continue

    def exec_for(self, stmt, env):
        iterable = self.eval_expr(stmt.iterable, env)
        for item in iterable:
            env.set(stmt.variable, item)
            try:
                self.exec_block(stmt.body, env)
            except BreakSignal:
                break
            except ContinueSignal:
                continue

    def exec_block(self, statements, env):
        for stmt in statements:
            self.exec_statement(stmt, env)

    def eval_expr(self, expr, env):
        if isinstance(expr, IntegerLiteral):
            return expr.value
        if isinstance(expr, FloatLiteral):
            return expr.value
        if isinstance(expr, StringLiteral):
            return self.interpolate_string(expr.value, env)
        if isinstance(expr, BooleanLiteral):
            return expr.value
        if isinstance(expr, ColorLiteral):
            return expr.value
        if isinstance(expr, Identifier):
            return env.get(expr.name)
        if isinstance(expr, BinaryOp):
            return self.eval_binary(expr, env)
        if isinstance(expr, UnaryOp):
            operand = self.eval_expr(expr.operand, env)
            if expr.operator == '-':
                return -operand
            if expr.operator == 'not':
                return not operand
            if expr.operator == '~':
                return ~operand
            return +operand
        if isinstance(expr, FunctionCall):
            return self.eval_call(expr, env)
        if isinstance(expr, ListLiteral):
            return [self.eval_expr(e, env) for e in expr.elements]
        if isinstance(expr, DictLiteral):
            return {self.eval_expr(k, env): self.eval_expr(v, env) for k, v in expr.pairs}
        if isinstance(expr, RecordLiteral):
            return self.eval_record(expr, env)
        if isinstance(expr, SetLiteral):
            return {self.eval_expr(e, env) for e in expr.elements}
        if isinstance(expr, TupleLiteral):
            return tuple(self.eval_expr(e, env) for e in expr.elements)
        if isinstance(expr, RangeExpression):
            start = self.eval_expr(expr.start, env)
            end = self.eval_expr(expr.end, env)
            if type(start) is not int or type(end) is not int:
                raise TypeError(f"Range bounds must be integers at {expr.line}:{expr.column}")
            return range(start, end)
        if isinstance(expr, MemberAccess):
            obj = self.eval_expr(expr.object, env)
            name = expr.member
            # Support dict dot access and built-in methods
            if isinstance(obj, dict):
                if name == 'keys':
                    return lambda: list(obj.keys())
                if name == 'values':
                    return lambda: list(obj.values())
                if name == 'items':
                    return lambda: list(obj.items())
                if name in obj:
                    return obj[name]
            if isinstance(obj, list):
                if name == 'append':
                    return lambda val: obj.append(val)
                if name == 'pop':
                    return lambda: obj.pop()
                if name == 'length':
                    return len(obj)
            if isinstance(obj, str):
                if name == 'length':
                    return len(obj)
                if name == 'upper':
                    return lambda: obj.upper()
                if name == 'lower':
                    return lambda: obj.lower()
                if name == 'split':
                    return lambda sep=" ": obj.split(sep)
                if name == 'strip':
                    return lambda: obj.strip()
                if name == 'replace':
                    return lambda old, new: obj.replace(old, new)
                if name == 'startswith':
                    return lambda prefix: obj.startswith(prefix)
                if name == 'endswith':
                    return lambda suffix: obj.endswith(suffix)
                if name == 'contains':
                    return lambda sub: sub in obj
            raise AttributeError(f"'{type(obj).__name__}' has no attribute '{name}'")
        if isinstance(expr, IndexAccess):
            obj = self.eval_expr(expr.object, env)
            index = self.eval_expr(expr.index, env)
            return obj[index]
        if isinstance(expr, VectorLiteral):
            if len(expr.components) != expr.dimension:
                raise TypeError(
                    f"vec{expr.dimension}: expected {expr.dimension} components, "
                    f"got {len(expr.components)} at {expr.line}:{expr.column}"
                )
            return tuple(self.eval_expr(c, env) for c in expr.components)
        raise RuntimeError(f"Unknown expression: {type(expr).__name__}")

    def eval_record(self, expr, env):
        record_type = env.get(expr.type_name)
        if not isinstance(record_type, RecordType):
            raise TypeError(f"'{expr.type_name}' is not a record type at {expr.line}:{expr.column}")

        definition = record_type.definition
        declared = {field.name for field in definition.fields}
        provided = {name for name, _ in expr.fields}
        unknown = provided - declared
        if unknown:
            raise TypeError(f"Unknown field(s) for {definition.name}: {', '.join(sorted(unknown))} at {expr.line}:{expr.column}")
        missing = [field.name for field in definition.fields
                   if field.name not in provided and field.default_value is None]
        if missing:
            raise TypeError(f"Missing required field(s) for {definition.name}: {', '.join(missing)} at {expr.line}:{expr.column}")

        # Validate shape before executing any initializer. Explicit values run
        # in source order at the call site, then omitted defaults in declaration
        # order at the defining scope. Annotations remain metadata, as elsewhere.
        values = {name: self.eval_expr(value, env) for name, value in expr.fields}
        for field in definition.fields:
            if field.name not in values:
                values[field.name] = self.eval_expr(field.default_value, record_type.environment)
        return {field.name: values[field.name] for field in definition.fields}

    def eval_binary(self, expr, env):
        left = self.eval_expr(expr.left, env)
        op = expr.operator
        # Logical guards evaluate the right operand only when needed, while
        # preserving the selected operand value rather than coercing to bool.
        if op == 'and':
            return self.eval_expr(expr.right, env) if left else left
        if op == 'or':
            return left if left else self.eval_expr(expr.right, env)
        right = self.eval_expr(expr.right, env)
        ops = {
            '+': lambda a, b: a+b, '-': lambda a, b: a-b,
            '*': lambda a, b: a*b, '/': lambda a, b: a/b,
            '%': lambda a, b: a%b, '**': lambda a, b: a**b,
            '==': lambda a, b: a==b, '!=': lambda a, b: a!=b,
            '<': lambda a, b: a<b, '>': lambda a, b: a>b,
            '<=': lambda a, b: a<=b, '>=': lambda a, b: a>=b,
            '&': lambda a, b: a & b, '|': lambda a, b: a | b,
            '^': lambda a, b: a ^ b,
        }
        if op in ops:
            return ops[op](left, right)
        raise RuntimeError(f"Unknown operator: {op}")

    def interpolate_string(self, s, env):
        """Handle {var} interpolation in strings"""
        import re
        def replacer(match):
            varname = match.group(1)
            try:
                return str(env.get(varname))
            except NameError:
                return match.group(0)
        return re.sub(r'\{(\w+)\}', replacer, s)

    def install_builtins(self):
        builtins = {
            'print': lambda args: print(*args),
            'len': lambda args: len(args[0]),
            'range': lambda args: range(*args),
            'str': lambda args: str(args[0]),
            'int': lambda args: int(args[0]),
            'float': lambda args: float(args[0]),
            'bool': lambda args: bool(args[0]),
            'type': lambda args: type(args[0]).__name__,
            'abs': lambda args: abs(args[0]),
            'min': lambda args: min(*args) if len(args) > 1 else min(args[0]),
            'max': lambda args: max(*args) if len(args) > 1 else max(args[0]),
            'sum': lambda args: sum(args[0]),
            'sorted': lambda args: sorted(args[0]),
            'reversed': lambda args: list(reversed(args[0])),
            'enumerate': lambda args: list(enumerate(args[0])),
            'zip': lambda args: list(zip(*args)),
            'input': lambda args: input(args[0] if args else ''),
            'list': lambda args: list(args[0]) if args else [],
            'dict': lambda args: dict(args[0]) if args else {},
            'set': lambda args: set(args[0]) if args else set(),
            'round': lambda args: round(args[0], args[1] if len(args) > 1 else 0),
            'chr': lambda args: chr(args[0]),
            'ord': lambda args: ord(args[0]),
            'hex': lambda args: hex(args[0]),
            'bin': lambda args: bin(args[0]),
            'isinstance': lambda args: isinstance(args[0], args[1]),
        }
        builtins['map'] = lambda args: self.execute_collection('map', args)
        builtins['filter'] = lambda args: self.execute_collection('filter', args)
        arities = {
            'print': (0, None), 'zip': (0, None),
            'min': (1, None), 'max': (1, None), 'range': (1, 3),
            'input': (0, 1), 'list': (0, 1), 'dict': (0, 1),
            'set': (0, 1), 'round': (1, 2), 'isinstance': (2, 2),
            'map': (2, None), 'filter': (2, 2),
        }
        for name, implementation in builtins.items():
            self.global_env.set(name, BuiltinFunction(
                name, implementation, *arities.get(name, (1, 1))))

    def validate_callable(self, func, supplied):
        if isinstance(func, BuiltinFunction):
            func.validate(supplied)
        elif isinstance(func, FunctionDefinition):
            self.validate_function_call(func, supplied)
        elif not callable(func):
            raise RuntimeError(f"'{func}' is not callable")

    def invoke_callable(self, func, args):
        """Invoke a validated callable with already evaluated arguments."""
        if isinstance(func, BuiltinFunction):
            return func.implementation(args)
        if isinstance(func, FunctionDefinition):
            return self.execute_function(func, args)
        return func(*args)

    def eval_call(self, expr, env):
        func = self.eval_expr(expr.function, env)
        self.validate_callable(func, len(expr.arguments))
        # Collection calls additionally validate the callback before input
        # expressions, including when map/filter were reached through aliases.
        if isinstance(func, BuiltinFunction) and func.name in {'map', 'filter'}:
            callback = self.eval_expr(expr.arguments[0], env)
            self.collection_callback(func.name, callback, len(expr.arguments) - 1)
            args = [callback] + [self.eval_expr(arg, env) for arg in expr.arguments[1:]]
        else:
            args = [self.eval_expr(arg, env) for arg in expr.arguments]
        return self.invoke_callable(func, args)

    def collection_callback(self, name, func, input_count):
        if not isinstance(func, (BuiltinFunction, FunctionDefinition)) and not callable(func):
            raise TypeError(f"{name}: first argument must be callable")
        self.validate_callable(func, input_count if name == 'map' else 1)
        return lambda *values: self.invoke_callable(func, list(values))

    def execute_collection(self, name, args):
        callback = self.collection_callback(name, args[0], len(args) - 1)
        if name == 'map':
            return list(map(callback, *args[1:]))
        return list(filter(callback, args[1]))

    def validate_function_call(self, func, supplied):
        """Validate a Road function before evaluating supplied argument expressions."""
        names = set()
        optional = False
        required = 0
        variadic = False
        for index, param in enumerate(func.parameters):
            if param.name in names:
                raise TypeError(f"{func.name}: duplicate parameter '{param.name}'")
            names.add(param.name)
            if param.is_variadic:
                if index != len(func.parameters) - 1 or param.default_value is not None:
                    raise TypeError(f"{func.name}: variadic parameter must be last and have no default")
                variadic = True
            elif param.default_value is not None:
                optional = True
            else:
                if optional:
                    raise TypeError(f"{func.name}: required parameter follows a default")
                required += 1
        maximum = len(func.parameters) - int(variadic)
        if supplied < required or (not variadic and supplied > maximum):
            expected = f"at least {required}" if variadic else f"{required}..{maximum}"
            raise TypeError(f"{func.name}: expected {expected} arguments, got {supplied}")

    def execute_function(self, func, args):
        """Execute a validated Road function with already evaluated values."""
        supplied = len(args)
        # Use closure environment if available, otherwise global
        parent_env = getattr(func, '_closure_env', self.global_env)
        call_env = Environment(parent=parent_env)
        for index, param in enumerate(func.parameters):
            if param.is_variadic:
                value = args[index:]
            elif index < supplied:
                value = args[index]
            else:
                value = self.eval_expr(param.default_value, call_env)
            call_env.set(param.name, value)

        try:
            self.exec_block(func.body, call_env)
        except ReturnSignal as ret:
            return ret.value
        except BreakSignal:
            raise RuntimeError(f"{func.name}: break outside a loop in this function") from None
        except ContinueSignal:
            raise RuntimeError(f"{func.name}: continue outside a loop in this function") from None
        return None
