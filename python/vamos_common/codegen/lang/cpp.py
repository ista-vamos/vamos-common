from ...types.type import Type, BoolType, IntType, UIntType, NumType, EventType


def cpp_type(ty: Type):
    assert isinstance(ty, Type), ty
    if isinstance(ty, BoolType):
        return "bool"
    if isinstance(ty, IntType):
        return f"int{ty.bitwidth}_t"
    if isinstance(ty, UIntType):
        return f"uint{ty.bitwidth}_t"
    if isinstance(ty, NumType):
        return "int"
    if isinstance(ty, EventType):
        return f"Event_{ty.name}"
    raise NotImplementedError(f"Unknown type: {ty}")
