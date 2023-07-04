from .element import Element


class Identifier(Element):
    def __init__(self, name, ty=None):
        super().__init__(ty=ty)
        self.name = name

    def is_identifier(self):
        return True

    def pretty_str(self):
        return self.name

    def __str__(self):
        return f"ID({self.name})" + (f": {self.type()}" if self.type() else "")

    def __eq__(self, other):
        assert isinstance(other, Identifier), (other, type(other))
        return self.name == other.name

    def __hash__(self):
        return self.name.__hash__()

    __repr__ = __str__

    @property
    def children(self):
        return ()