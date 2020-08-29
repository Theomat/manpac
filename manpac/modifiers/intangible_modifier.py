from manpac.utils import export
from manpac.modifiers.abstract_modifier import AbstractModifier


@export
class IntangibleModifier(AbstractModifier):
    """
    Represents a intangible modifier boost.
    """
    @property
    def is_tangible(self):
        return False
