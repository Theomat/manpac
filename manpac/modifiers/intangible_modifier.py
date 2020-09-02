from manpac.utils import export
from manpac.modifiers.abstract_modifier import AbstractModifier
from manpac.direction import Direction


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
        new_pos = self.game.map.closest_walkable(entity.pos) + .5
        for direction in Direction.representing(new_pos - entity.pos):
            new_pos -= direction.vector * (.5 - entity.size)
        entity.teleport(new_pos)
