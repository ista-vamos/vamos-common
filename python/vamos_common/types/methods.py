class MethodHeader:
    """
    An object describing the type of methods and its name.
    It contains also associated methods for typing and similar.
    """

    def __init__(self, name, types, retty, typing_rule=None):
        """
        :types: are types of parameters
        """
        self.name = name
        self.types = types
        self.retty = retty
        self.typing_rule = typing_rule

    def __repr__(self):
        return f"MethodHeader({self.name}, {self.types}, {self.retty})"
