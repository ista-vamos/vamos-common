from lark import Transformer
from vamos_common.parser.context import Context
from vamos_common.spec.ir.constant import Constant
from vamos_common.spec.ir.decls import DataField, EventDecl
from vamos_common.spec.ir.identifier import Identifier
from vamos_common.types.type import (
    NumType,
    type_from_token,
    UserType,
    EventType,
    TraceType,
    HypertraceType,
    Type,
    StringType,
    TupleType,
)

from ..spec.ir.expr import (
    BoolExpr,
    Expr,
    IsIn,
    CompareExpr,
    Cast,
    BinaryOp,
    Event,
    TupleExpr,
    CommandLineArgument,
)


class BaseTransformer(Transformer):
    def __init__(self, ctx=None):
        super().__init__()
        self.ctx = ctx or Context()

    # def NUMBER(self, items):
    #    return Constant(int(items.value), NumType())
    def constant_tuple(self, items):
        return TupleExpr(items, TupleType([it._type for it in items]))

    def constant_string(self, items):
        # strip quotes from the string
        return Constant(items[0][1:-1], StringType())

    def constant_number(self, items):
        ty = items[1] if len(items) > 1 else NumType()
        return Constant(int(items[0]), ty)

    def constant(self, items):
        assert len(items) == 1
        assert isinstance(items[0], Expr), items[0]
        return items[0]

    def NAME(self, items):
        return Identifier(str(items.value))


class ProcessTypes(BaseTransformer):
    def simpletype(self, items):
        assert len(items) == 1, items
        return type_from_token(items[0])

    def usertype(self, items):
        assert isinstance(items[0], Identifier), items[0]
        name = items[0].name
        if self.ctx.get_eventdecl(name):
            return EventType(name)
        return UserType(name)

    def tracetype(self, items):
        return TraceType(items)

    def hypertracetype(self, items):
        return HypertraceType(items)

    def type(self, items):
        return items[0]


class ProcessEvents(BaseTransformer):
    def __init__(self, ctx):
        super().__init__(ctx)

    def datafield(self, items):
        name = items[0].children[0]
        ty = items[1].children[0]
        assert isinstance(ty, Type), items[1]
        return DataField(name, ty)

    def fieldsdecl(self, items):
        return items

    def eventdecl(self, items):
        names = items[0].children
        fields = items[1] if len(items) > 1 else []

        decls = []
        for name in names:
            ev = EventDecl(name, fields)
            self.ctx.add_eventdecl(ev)
            decls.append(ev)
        return decls


class ProcessExpr(BaseTransformer):
    def __init__(self, ctx=None):
        super().__init__(ctx)

    def boolexpr(self, items):
        assert len(items) == 1, items
        assert isinstance(items[0], BoolExpr), items
        return items[0]

    def _compare(self, comp, items):
        assert len(items) == 2, items
        return CompareExpr(comp, items[0], items[1])

    def eq(self, items):
        return self._compare("==", items)

    def ne(self, items):
        return self._compare("!=", items)

    def le(self, items):
        return self._compare("<=", items)

    def ge(self, items):
        return self._compare(">=", items)

    def lt(self, items):
        return self._compare("<", items)

    def gt(self, items):
        return self._compare(">", items)

    def compareexpr(self, items):
        assert len(items) == 1, items
        return items[0]

    #   def land(self, items):
    #       if len(items) == 1:
    #           return items[0]
    #       return And(items[0], items[1])
    #
    #   def lor(self, items):
    #       if len(items) == 1:
    #           return items[0]
    #       return Or(items[0], items[1])
    #
    #   def constexpr(self, items):
    #       assert isinstance(items[0], ConstExpr), items
    #       return items[0]
    #
    #   def labelexpr(self, items):
    #       return Label(items[0])
    #
    #   def subwordexpr(self, items):
    #       return SubWord(items[0], items[1])

    def is_in(self, items):
        lhs = items[0]
        assert isinstance(lhs, (Expr, Identifier)), lhs

        rhs = items[1] if isinstance(items[1], Expr) else items[1].children[0]
        assert isinstance(rhs, (Expr, Identifier)), rhs
        return IsIn(lhs, rhs)

    def add(self, items):
        return BinaryOp("+", items[0], items[1])

    def mul(self, items):
        return BinaryOp("*", items[0], items[1])

    def cast(self, items):
        assert len(items) == 2
        return Cast(items[0], items[1])

    def expr(self, items):
        if isinstance(items[0], Expr):
            return items[0]

        # this is an identifier
        assert items[0].data == "name", items
        assert len(items[0].children) == 1, items[0]
        assert isinstance(items[0].children[0], Identifier), items[0]
        return items[0].children[0]

    def cmdarg(self, items):
        return CommandLineArgument(items[0])

    def event(self, items):
        name = items[0].children[0]
        params = []
        for p in items[1] or ():
            if isinstance(p, Expr):
                params.append(p)
            else:
                assert p.data == "name", p
                params.append(p.children[0])
        assert isinstance(name, Identifier), name
        return Event(self.ctx.get_eventdecl(name), name.name, params)


def visit_ast(node, lvl, fn, *args):
    fn(lvl, node, *args)
    if node is None:
        return

    if not hasattr(node, "children"):
        return
    for ch in node.children:
        visit_ast(ch, lvl + 1, fn, args)


def visit_ast_dfs(node, lvl, fn, *args):
    if node is None:
        return
    # if not hasattr(node, "children"):
    #    return

    for ch in node.children:
        visit_ast_dfs(ch, lvl + 1, fn, args)

    fn(lvl, node, *args)


def visit_dfs(ast, fn, *args):
    visit_ast_dfs(ast, 0, fn, *args)
