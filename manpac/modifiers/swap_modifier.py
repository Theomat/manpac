from manpac.utils import export
from manpac.modifiers.abstract_modifier import AbstractModifier


@export
class SwapModifier(AbstractModifier):
    """
    Represents a swap modifier boost.
    """

    def __init__(self, game, range, duration=30):
        super(SwapModifier, self).__init__(game, duration)
        self.range = range

    def on_death(self, caster):
        # Find closest entity in range
        closest = None
        distance = 1e12
        for entity in self.game.entities:
            if not entity.alive or not entity.is_tangible:
                continue
            d = caster.squared_distance_to(entity.pos)
            if d > 0 and d <= self.range * self.range and d <= distance:
                distance = d
                closest = entity
        # Swap positions
        if closest:
            copy = caster.pos.copy()
            caster.teleport(closest.pos)
            closest.teleport(copy)
