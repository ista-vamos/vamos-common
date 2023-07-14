from ..spec.ir.identifier import Identifier


class NewTraceSpec:
    def __init__(self, name, outputs):
        self.name = name
        self.outputs = outputs

    def is_stdout(self):
        return "stdout" in self.outputs


class Context:
    def __init__(self):
        self.decls = {}
        self.eventdecls = {}
        self.usertypes = {}
        self.tracetypes = {}
        # mapping of identifiers and elements in general to types
        self.types = {}
        self._modules = {}

        # self.decls = ctx.get('decls') if ctx else {}
        # self.eventdecls = ctx.get('eventdecls') if ctx else {}
        # self.usertypes = ctx.get('usertypes') if ctx else {}

    def add_module(self, name, mod):
        if isinstance(name, Identifier):
            name = name.name
        assert isinstance(name, str), name
        assert name not in self._modules, (name, self._modules)
        self._modules[name] = mod

    def add_tracetype(self, ty, outputs):
        """
        Generate the name for trace type. Same (compatible) trace types have the same name
        (as determined by the __eq__ method on TraceType class).

        :return: str with a name of the trace.
        """
        if not ty in self.tracetypes:
            self.tracetypes[ty] = NewTraceSpec(f"Trace_{len(self.tracetypes)}", outputs)

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

    def alphabet(self):
        return list(self.eventdecls.values())

    def get_module(self, name):
        if isinstance(name, Identifier):
            name = name.name
        return self._modules.get(name)

    def get_method(self, mod, name):
        if isinstance(name, Identifier):
            name = name.name
        if isinstance(mod, (str, Identifier)):
            mod = self.get_module(mod)

        assert mod is not None, (name, self._modules)
        assert isinstance(name, str)
        return mod.METHODS[name]

    def dump(self):
        print(self, ":")
        print("Decls     :", self.decls)
        print("EventDecls:", self.eventdecls)
        print("UTypes    :", self.usertypes)
        print("TTypes    :", self.usertypes)
