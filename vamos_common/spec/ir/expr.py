from vamos_common.types.type import (
    EventType,
    STRING_TYPE,
    BOOL_TYPE,
)

from ..ir.element import Element


class Expr(Element):
    """
    Class representing an expression in the language
    """


class TupleExpr(Expr):
    def __init__(self, vals, ty):
        super().__init__(ty)
        self.values = vals

    def __repr__(self):
        return f"TupleExpr({','.join(map(str, self.values))})"

    @property
    def children(self):
        return self.values


class Cast(Expr):
    def __init__(self, val, ty):
        super().__init__(ty)
        self._value = val

    @property
    def value(self):
        return self._value

    def pretty_str(self):
        return f"{self.value} as {self.type()}"

    def __repr__(self):
        return f"Cast({self.value}, {self.type()})"

    @property
    def children(self):
        return ()

    def typing_rule(self, types):
        types.assign(self, self.type())


class CommandLineArgument(Expr):
    """
    Argument to the specification from the command line ($1, $2, ...)
    """

    def __init__(self, n):
        super().__init__(STRING_TYPE)
        self.num = n

    def __repr__(self):
        return f"CommandLineArgument({self.num})"

    @property
    def children(self):
        return ()

    def typing_rule(self, types):
        types.assign(self, STRING_TYPE)


class BoolExpr(Expr):
    def __init__(self):
        super().__init__(BOOL_TYPE)

    @property
    def children(self):
        return ()

    def typing_rule(self, types):
        types.assign(self, BOOL_TYPE)


class And(BoolExpr):
    def __init__(self, lhs, rhs):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs

    def pretty_str(self):
        return f"({self.lhs.pretty_str()} && {self.rhs.pretty_str()})"

    def __str__(self):
        return f"({self.lhs} && {self.rhs})"

    def __repr__(self):
        return f"And({self.lhs} && {self.rhs})"

    @property
    def children(self):
        return [self.lhs, self.rhs]

    def typing_rule(self, types):
        types.assign(self, BOOL_TYPE)
        types.assign(self.lhs, BOOL_TYPE)
        types.assign(self.rhs, BOOL_TYPE)


class Or(BoolExpr):
    def __init__(self, lhs, rhs):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs

    def pretty_str(self):
        return f"({self.lhs.pretty_str()} || {self.rhs.pretty_str()})"

    def __str__(self):
        return f"({self.lhs} || {self.rhs})"

    def __repr__(self):
        return f"Or({self.lhs} || {self.rhs})"

    @property
    def children(self):
        return [self.lhs, self.rhs]

    def typing_rule(self, types):
        types.assign(self, BOOL_TYPE)
        types.assign(self.lhs, BOOL_TYPE)
        types.assign(self.rhs, BOOL_TYPE)


class CompareExpr(BoolExpr):
    def __init__(self, comparison, lhs, rhs):
        super().__init__()
        self.comparison = comparison
        self.lhs = lhs
        self.rhs = rhs

    def pretty_str(self):
        return f"{self.lhs.pretty_str()} {self.comparison} {self.rhs.pretty_str()}"

    def __str__(self):
        return f"{self.lhs} {self.comparison} {self.rhs}"

    def __repr__(self):
        return f"CompareExpr({self.lhs} {self.comparison} {self.rhs})"

    @property
    def children(self):
        return [self.lhs, self.rhs]

    def typing_rule(self, types):
        types.assign(self, BOOL_TYPE)
        types.assign(self.lhs, types.get(self.rhs))
        types.assign(self.rhs, types.get(self.lhs))


class IsIn(BoolExpr):
    def __init__(self, lhs, rhs):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs

    def pretty_str(self):
        return f"{self.lhs.pretty_str()} in {self.rhs.pretty_str()}"

    def __repr__(self):
        return f"IsIn({self.lhs}, {self.rhs})"

    @property
    def children(self):
        return [self.lhs, self.rhs]

    def typing_rule(self, types):
        types.assign(self, BOOL_TYPE)
        types.assign(self.lhs, self.rhs.iterator_type().elem_type())
        lhs_ty = types.get(self.lhs)
        if lhs_ty:
            types.assign(self.rhs, IterableType(IteratorType(lhs_ty)))


class Event(Expr):
    def __init__(self, decl, name, params):
        assert isinstance(name, str), name
        super().__init__(EventType(name))
        self.decl = decl
        self.name = name
        self.params = params

        assert decl is None or decl.name.name == name, (decl, name)

    def __repr__(self):
        return f"Event({self.name}, {self.params})"

    @property
    def children(self):
        return self.params or ()

    def typing_rule(self, types):
        types.assign(self, self.type())
        for param, field in zip(self.params, self.decl.fields):
            types.assign(param, field.type())


class BinaryOp(Expr):
    def __init__(self, op, lhs, rhs):
        super().__init__()
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def pretty_str(self):
        return f"({self.lhs.pretty_str()} {self.op} {self.rhs.pretty_str()})"

    def __repr__(self):
        return f"BinaryOp({self.op}, {self.lhs}, {self.rhs})"

    @property
    def children(self):
        return [self.lhs, self.rhs]

    def typing_rule(self, types):
        types.assign(self, types.get(self.lhs.type()))
        types.assign(self, types.get(self.rhs.type()))
        types.assign(self.lhs, types.get(self.rhs.type()))
        types.assign(self.rhs, types.get(self.rhs.type()))
        types.assign(self.lhs, types.get(self))
        types.assign(self.rhs, types.get(self))