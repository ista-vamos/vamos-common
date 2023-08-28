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

    def typing_rule(self, types):
        """
        This method allows to implement typing rules for the element.
        It is used by the type-checker to infer types.

        :param types: object that has methods `get` and `assign`. `get(elem)` gets the current type
        (if any) that is assigned to a given `elem` and `assign(elem, ty)` asserts that the element
        `elem` has type `ty`. It has also the method `visit(elem)` that can be used to explicitely (and recursively)
        typecheck a given `elem`. It is needed in cases when some elements that should be type-checked
        are not among childrens of an element.
        """
        raise NotImplementedError(
            f"Children must override this method: {self} : {type(self)}"
        )


class ElementList(list):
    @property
    def children(self):
        return self

    def __repr__(self):
        return f"List{super().__repr__()}"
