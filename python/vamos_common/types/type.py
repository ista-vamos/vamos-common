class Type:
    methods = {}

    @property
    def children(self):
        raise NotImplementedError(f"Must be overriden for {self}")

    def unify(self, other):
        raise NotImplementedError(f"Must be overriden for {self}")

    def __eq__(self, other):
        return isinstance(other, type(self))

    def __hash__(self):
        return hash(self.__repr__())

    def get_method(self, name: str):
        assert isinstance(name, str), name
        return type(self).methods.get(name)


class UserType(Type):
    def __init__(self, name):
        super().__init__()
        assert isinstance(name, str), name
        self.name = name

    def __str__(self):
        return f"uTYPE({self.name})"

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.name == other.name

    def __hash__(self):
        return hash(str(self))

    @property
    def children(self):
        return ()

    def unify(self, other):
        if self != other:
            raise NotImplementedError(f"{self} cannot by unified with {other}")
        return self


class EventType(UserType):
    def __str__(self):
        return f"EventTy({self.name})"

    def __repr__(self):
        return f"EventType({self.name})"

    def __eq__(self, other):
        return isinstance(other, EventType) and self.name == other.name

    def __hash__(self):
        return hash(self.__repr__())

    def unify(self, other):
        if self != other:
            raise NotImplementedError(f"{self} cannot by unified with {other}")
        return self


class SimpleType(Type):
    @property
    def children(self):
        return ()

    def unify(self, other):
        if not isinstance(other, BoolType):
            raise NotImplementedError(f"{self} cannot by unified with {other}")
        return self


class BoolType(SimpleType):
    def __str__(self):
        return "Bool"


BOOL_TYPE = BoolType()


class NumType(SimpleType):
    def __init__(self, bitwidth=None):
        super().__init__()
        assert bitwidth is None or bitwidth in (8, 16, 32, 64), bitwidth
        self.bitwidth = bitwidth

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.bitwidth == other.bitwidth

    def __hash__(self):
        return hash(self.__repr__())

    def __repr__(self):
        if self.bitwidth is None:
            return "NumTy(?)"
        return f"NumTy({self.bitwidth})"

    def unify(self, other):
        if issubclass(type(other), NumType):
            return other
        elif isinstance(other, NumType):
            return self
        raise NotImplementedError(f"{self} cannot by unified with {other}")


class IntType(NumType):
    def __init__(self, bitwidth):
        super().__init__(bitwidth)
        self.signed = True

    def __str__(self):
        return f"Int{self.bitwidth}"

    def unify(self, other):
        if type(other) == NumType or self == other:
            return self
        raise NotImplementedError(f"{self} cannot by unified with {other}")


class UIntType(NumType):
    def __init__(self, bitwidth):
        super().__init__(bitwidth)
        self.signed = False

    def __str__(self):
        return f"UInt{self.bitwidth}"

    def unify(self, other):
        if type(other) == NumType or self == other:
            return self
        raise NotImplementedError(f"{self} cannot by unified with {other}")


class IteratorType(Type):
    def __init__(self, elem_ty):
        self._elem_ty = elem_ty

    def __eq__(self, other):
        return isinstance(other, IteratorType) and self._elem_ty == other._elem_ty

    def __repr__(self):
        return f"IteratorTy({self._elem_ty})"

    def elem_ty(self):
        return self._elem_ty

    @property
    def children(self):
        return ()

    def unify(self, other):
        if isinstance(other, IteratorType):
            return IteratorType(self.elem_ty().unify(other.elem_ty()))
        raise NotImplementedError(f"{self} cannot by unified with {other}")


class OutputType(Type):
    """
    Type of object that serve as output of traces
    """

    @property
    def children(self):
        return ()


class IterableType(Type):
    @property
    def children(self):
        return ()


ITERABLE_TYPE = IterableType()


class TraceType(IterableType):
    def __init__(self, subtypes):
        super().__init__()
        assert all(
            map(lambda ty: isinstance(ty, (SimpleType, UserType)), subtypes)
        ), subtypes
        self.subtypes = set(subtypes)

    def __str__(self):
        return f"Tr:{','.join(map(str, self.subtypes))}"

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.subtypes == other.subtypes

    def __hash__(self):
        return hash(str(self))

    @property
    def children(self):
        return self.subtypes

    def unify(self, other):
        if self == other:
            return self
        raise NotImplementedError(f"{self} cannot by unified with {other}")


class HypertraceType(IterableType):
    def __init__(self, subtypes, bounded=True):
        super().__init__()
        assert all(
            map(lambda ty: isinstance(ty, (TraceType, UserType)), subtypes)
        ), subtypes
        self.subtypes = subtypes
        self.bounded = bounded

    def __str__(self):
        return f"Ht:{{{','.join(map(str, self.subtypes))} {'...' if not self.bounded else ''}}}"

    def __eq__(self, other):
        return (
            isinstance(other, type(self))
            and self.subtypes == other.subtypes
            and self.bounded == other.bounded
        )

    @property
    def children(self):
        return self.subtypes

    def unify(self, other):
        if self == other:
            return self
        raise NotImplementedError(f"{self} cannot by unified with {other}")


def int_type_from_token(token):
    if token == "Int64":
        return IntType(64)
    if token == "Int32":
        return IntType(32)
    if token == "Int8":
        return IntType(8)
    if token == "Int16":
        return IntType(16)

    raise NotImplementedError(f"Invalid type: {token}")


def uint_type_from_token(token):
    if token == "UInt64":
        return UIntType(64)
    if token == "UInt32":
        return UIntType(32)
    if token == "UInt8":
        return UIntType(8)
    if token == "UInt16":
        return UIntType(16)

    raise NotImplementedError(f"Invalid type: {token}")


def type_from_token(token):
    if token == "Bool":
        return BoolType()

    if token.startswith("Int"):
        return int_type_from_token(token)

    if token.startswith("UInt"):
        return uint_type_from_token(token)

    raise NotImplementedError(f"Unknown type: {token}")


class TupleType(IterableType):
    def __init__(self, elems_tys):
        super().__init__()
        self.subtypes = elems_tys

    def __repr__(self):
        return f"TupleTy({', '.join(map(str, self.subtypes))})"


class StringType(IterableType):
    methods = {}

    def __init__(self):
        super().__init__()

    def __repr__(self):
        return "StringTy"

    @property
    def children(self):
        return ()


STRING_TYPE = StringType()


class ObjectType(Type):
    def __repr__(self):
        return "ObjectTy"

    @property
    def children(self):
        return ()


OBJECT_TYPE = ObjectType()
