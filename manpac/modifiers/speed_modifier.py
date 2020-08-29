from manpac.utils import export
from manpac.modifiers.abstract_modifier import AbstractModifier


@export
class SpeedModifier(AbstractModifier):
    """
    Represents a speed modifier boost.
    """

    def __init__(self, game, duration, multiplier):
        super(SpeedModifier, self).__init__(game, duration)
        self.multiplier = multiplier

    @property
    def speed_multiplier(self):
        return self.multiplier
