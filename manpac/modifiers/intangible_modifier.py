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

    def on_death(self, entity):
        super(IntangibleModifier, self).on_death(entity)
        if not entity.is_tangible:
            return
        self.game.map.teleport_back_on_map(entity)
