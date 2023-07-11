from ..spec.ir.identifier import Identifier


class Context:
    def __init__(self):
        self.decls = {}
        self.eventdecls = {}
        self.usertypes = {}
        self.tracetypes = {}

        # self.decls = ctx.get('decls') if ctx else {}
        # self.eventdecls = ctx.get('eventdecls') if ctx else {}
        # self.usertypes = ctx.get('usertypes') if ctx else {}

    def add_tracetype(self, ty):
        """
        Generate the name for trace type. Same (compatible) trace types have the same name
        (as determined by the __eq__ method on TraceType class).

        :return: str with a name of the trace.
        """
        if not ty in self.tracetypes:
            self.tracetypes[ty] = f"TraceTy_{len(self.tracetypes)}"

        return self.tracetypes[ty]

    def get_tracetype(self, ty):
        return self.tracetypes.get(ty)

    def add_eventdecl(self, *decls):
        for decl in decls:
            self._add_eventdecl(decl.name, decl)

    def _add_eventdecl(self, name, decl):
        if isinstance(name, Identifier):
            name = name.name

        assert isinstance(name, str), (name, type(name))
        if name in self.eventdecls:
            raise RuntimeError(f"Repeated declaration of an event: {decl}")

        self.eventdecls[name] = decl
        assert self.get_eventdecl(name) is decl

    def get_eventdecl(self, name):
        if isinstance(name, Identifier):
            name = name.name
        assert isinstance(name, str), (name, type(name))
        return self.eventdecls.get(name)

    def dump(self):
        print(self, ":")
        print("Decls     :", self.decls)
        print("EventDecls:", self.eventdecls)
        print("UTypes    :", self.usertypes)
        print("TTypes    :", self.usertypes)
