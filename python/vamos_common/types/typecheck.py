from ..spec.ir.identifier import Identifier
from .type import Type
from ..parser.ast import visit_dfs


class TypeCheckerProxy:
    """
    An instance of this class is passed to `typing_rule`
    method of elements so that they can assert
    facts about types.
    """

    def __init__(self, typechecker):
        self._typechecker = typechecker

    def assign(self, elem, ty):
        return self._typechecker.assign(elem, ty)

    def get(self, elem):
        return self._typechecker.get(elem)

    def visit(self, node):
        self._typechecker.visit(node)

    def dump(self):
        for i, t in self._typechecker.types().items():
            print(":: ", i, ": ", t)


class TypeChecker:
    def __init__(self, ctx):
        self._ctx = ctx
        self._types = {}
        self._proxy = TypeCheckerProxy(self)
        self._changed = False

    def get(self, elem):
        return self._types.get(elem)

    def assign(self, elem, ty):
        print("\033[36;1m[TC] assign", elem, "~>", ty, "\033[0m")
        assert ty is None or isinstance(ty, Type), (elem, ty)
        if ty is None:
            # register that we have tried assigned None to this element
            if elem not in self._types:
                self._types[elem] = None
            return False

        changed = False
        cur_ty = self._types.get(elem)
        if cur_ty:
            print(">> ", cur_ty, ty)
            new_ty = cur_ty.unify(ty)
            changed = new_ty != cur_ty
            self._changed = changed
            self._types[elem] = new_ty
            assert self.get(elem) == new_ty
        else:
            self._types[elem] = ty
            assert self.get(elem) == ty
            self._changed = True
            changed = True
        if changed:
            print("\033[31;1m[TC]", elem, f": {cur_ty} ~> ", ty, "\033[0m")
        return changed

    def _visit_node(self, lvl, node, *args):
        if isinstance(node, (Type, Identifier)):
            return
        print("[TC]", " " * lvl, node)
        node.typing_rule(self._proxy)

    def typecheck(self, ast):
        self.visit(ast)
        while self._changed:
            self.visit(ast)

    def visit(self, node):
        """
        Recursively visit a given node.
        :param node:
        """
        visit_dfs(node, self._visit_node)

    def types(self):
        return self._types
