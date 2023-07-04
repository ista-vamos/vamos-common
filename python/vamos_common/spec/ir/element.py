class Element:
    def __init__(self, ty=None):
        self._type = ty

    def type(self):
        return self._type

    def is_identifier(self):
        return False

    @property
    def children(self):
        raise NotImplementedError(
            f"Children must override this property: {self} : {type(self)}"
        )


class ElementList(list):
    @property
    def children(self):
        return self

    def __repr__(self):
        return f"List{super().__repr__()}"
