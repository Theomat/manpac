from manpac.utils import export
from manpac.modifiers.abstract_modifier import AbstractModifier


@export
class GhostBlockModifier(AbstractModifier):
    """
    Represents a intangible modifier boost.
    """
    @property
    def can_ghost_collide(self):
        return True
