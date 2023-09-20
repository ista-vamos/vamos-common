class Type:
    """
    A type of elements in the specification
    """

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
        """Get the header of a type-associated method"""
        assert isinstance(name, str), name
        if name not in type(self).methods:
            raise RuntimeError(f"`{self}` has no method `{name}`")
        return type(self).methods[name]

    def is_user(self):
        "Is this a user-defined type?"
        return False

    def is_event(self):
        return False

    def is_bool(self):
        return False

    def is_num(self):
        return False

    def is_int(self):
        return False

    def is_uint(self):
        return False

    def is_string(self):
        return False


class UserType(Type):
    """
    A type defined by the user, e.g. and event
    """

    def __init__(self, name):
        super().__init__()
        assert isinstance(name, str), name
        self.name = name

    def is_user(self):
        return True

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
    def is_event(self):
        return True

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

    def is_bool(self):
        return True


BOOL_TYPE = BoolType()


class NumType(SimpleType):
    def __init__(self, bitwidth=None):
        super().__init__()
        assert bitwidth is None or bitwidth in (8, 16, 32, 64), bitwidth
        self.bitwidth = bitwidth

    def is_num(self):
        return True

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

    def is_int(self):
        return True

    def __repr__(self):
        return f"Int{self.bitwidth}"

    def unify(self, other):
        if type(other) == NumType or self == other:
            return self
        raise NotImplementedError(f"{self} cannot by unified with {other}")


class UIntType(NumType):
    def __init__(self, bitwidth):
        super().__init__(bitwidth)
        self.signed = False

    def is_uint(self):
        return True

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

    def has_fixed_len(self):
        return False

    def len(self):
        return None

    def is_tuple(self):
        return False

    def has_single_element(self):
        """
        Return True if this type of iterator iterates over a single type
        of element only. The default is True.
        """
        return True

    def elem_ty(self):
        assert isinstance(self._elem_ty, Type), self._elem_ty
        return self._elem_ty

    @property
    def children(self):
        return ()

    def unify(self, other):
        if isinstance(other, IteratorType):
            return IteratorType(self.elem_ty().unify(other.elem_ty()))
        raise NotImplementedError(f"{self} cannot by unified with {other}")


class TupleIteratorType(IteratorType):
    def __init__(self, elems_ty):
        if not isinstance(elems_ty, list):
            assert isinstance(elems_ty, tuple), elems_ty
            assert isinstance(elems_ty[0], Type), elems_ty
            assert isinstance(elems_ty[1], int), elems_ty
            elems_ty = [elems_ty[0]] * elems_ty[1]
        assert isinstance(elems_ty, list), elems_ty
        assert all((isinstance(ty, Type) for ty in elems_ty)), elems_ty
        super().__init__(elems_ty)

    def __eq__(self, other):
        return isinstance(other, TupleIteratorType) and self._elem_ty == other._elem_ty

    def __repr__(self):
        return f"TupleIteratorTy({self.elems_ty()})"

    def has_fixed_len(self):
        return True

    def len(self):
        return len(self.elems_ty())

    def is_tuple(self):
        return True

    def has_single_element(self):
        tys = self.elems_ty()
        return all((ty == tys[0] for ty in tys))

    def elem_ty(self):
        if self.has_single_element():
            assert isinstance(self._elem_ty, list), self._elem_ty
            return self.elems_ty()[0]

    def elems_ty(self):
        return self._elem_ty

    @property
    def children(self):
        return ()

    def unify(self, other):
        if isinstance(other, TupleIteratorType):
            return TupleIteratorType(
                [ty.unify(ty2) for ty, ty2 in zip(self.elems_ty(), other.elems_ty())]
            )
        raise NotImplementedError(f"{self} cannot by unified with {other}")


class IterableType(Type):
    """
    A type whose objects we can iterate via an iterator.
    """

    def __init__(self, iterator_type):
        assert isinstance(iterator_type, IteratorType), iterator_type
        self._iterator_type = iterator_type

    def iterator_type(self):
        return self._iterator_type

    @property
    def children(self):
        return ()

    def unify(self, other):
        if (
            isinstance(other, IterableType)
            and self._iterator_type == other._iterator_type
        ):
            if issubclass(type(other), type(self)):
                return other
            return self
        raise NotImplementedError(f"{self} cannot by unified with {other}")


class StringType(IterableType):
    methods = {}

    def __init__(self):
        super().__init__(IteratorType(UIntType(8)))

    def is_string(self):
        return True

    def __repr__(self):
        return "StringTy"

    @property
    def children(self):
        return ()


# def unify(self, other):
#    if type(self) == type(other):
#        return self
#    raise NotImplementedError(f"{self} cannot by unified with {other}")


STRING_TYPE = StringType()


class MultiType(Type):
    """
    Type that (may) consists of multiple types, e.g., a tuple or a trace of events
    """

    def __init__(self, subtypes):
        super().__init__()
        self._subtypes = subtypes

    def subtypes(self):
        return self._subtypes

    @property
    def children(self):
        return self._subtypes


class TraceType(MultiType):
    def __init__(self, subtypes):
        super().__init__(subtypes)
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


class HypertraceType(MultiType):
    def __init__(self, subtypes, bounded=True):
        super().__init__(subtypes)
        assert all(map(lambda ty: isinstance(ty, TraceType), subtypes)), subtypes
        self.subtypes = set(subtypes)
        self.bounded = bounded

    def __str__(self):
        return f"Ht:{{{','.join(map(str, self.subtypes))} {'...' if not self.bounded else ''}}}"

    def __eq__(self, other):
        return (
            isinstance(other, type(self))
            and self.subtypes == other.subtypes
            and self.bounded == other.bounded
        )

    def __hash__(self):
        return hash(str(self))

    @property
    def children(self):
        return self.subtypes

    def unify(self, other):
        if self == other:
            return self
        raise NotImplementedError(f"{self} cannot by unified with {other}")


class TupleType(MultiType):
    def __init__(self, elems_tys):
        assert isinstance(elems_tys, list), "The types for tuple must be ordered"
        super().__init__(elems_tys)

    def iterator_type(self):
        return TupleIteratorType(self.subtypes())

    def __repr__(self):
        return f"TupleTy({', '.join(map(str, self._subtypes))})"

    def unify(self, other):
        if isinstance(other, TupleType):
            return TupleType(
                [ty.unify(ty2) for ty, ty2 in zip(self.subtypes(), other.subtypes())]
            )
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


class ObjectType(Type):
    def __repr__(self):
        return "ObjectTy"

    @property
    def children(self):
        return ()


OBJECT_TYPE = ObjectType()


class OutputType(Type):
    """
    Type of object that serve as output of traces
    """

    @property
    def children(self):
        return ()


def type_from_token(token):
    if token == "Bool":
        return BoolType()

    if token.startswith("Int"):
        return int_type_from_token(token)

    if token.startswith("UInt"):
        return uint_type_from_token(token)

    if token == "String":
        return STRING_TYPE

    raise NotImplementedError(f"Unknown type: {token}")
