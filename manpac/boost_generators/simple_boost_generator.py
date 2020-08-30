from manpac.utils import export
from manpac.entity_type import EntityType
from manpac.utils.buffered_random import BufferedRandom

import numpy as np


@export
class SimpleBoostGenerator():
    """
    Represents a boost generator.

    Parameters
    -----------
    - *game*: (**Game**)
        the game this generator will be used in
    - *boost_probability*: (**float**)
        the probability at each tick of spawning a boost
    - *ghost_modifier_factory*: (**(float, () -> AbstractModifier) list**)
    - *pacman_modifier_factory*: (**(float, () -> AbstractModifier) list**)
        a list of (odds, factory) to generate the modifiers
    """

    def __init__(self, game, boost_probability, ghost_modifier_factory, pacman_modifier_factory):
        self.game = game
        self.boost_probability = boost_probability
        self._last_generation = 0
        self.rand = BufferedRandom(100)
        self.ghost_modifier_factory = ghost_modifier_factory
        self.pacman_modifier_factory = pacman_modifier_factory

    def _pick_boost_location_(self):
        """
        Pick a boost location.

        Return
        -----------
        A location for a boost to spawn
        type: **numpy.ndarray**
        """
        pos = np.array([-10, -10])
        while not self.game.map.is_walkable(pos):
            pos[0] = self.rand.randint(0, self.game.map.width - 1)
            pos[1] = self.rand.randint(0, self.game.map.height - 1)
        return pos

    def generate(self, ticks):
        """
        Try to generate boosts.

        Parameters
        -----------
        - *ticks*: (**float**)
            the number of ticks elapsed since last call

        Return
        -----------
        A list of locations where boosts should spawn.
        type: **numpy.ndarray list**
        """
        locations = []
        self._last_generation += ticks
        while self._last_generation > 1:
            if self.rand.uniform() <= self.boost_probability:
                locations.append(self._pick_boost_location_())
            self._last_generation -= 1
        return locations

    def make_modifier(self, entity, loc):
        """
        Produce a modifier for the specified entity that picked up a boost at the specified location.

        Parameters
        -----------
        - *entity*: (**Entity**)
            the entity to make a modifier for
        - *loc*: (**numpy.ndarray**)
            the location where the entity picked up the boost

        Return
        ----------
        A modifier to give to the entity.
        type: **AbstractModifier**
        """
        factory = self.ghost_modifier_factory
        if entity.type is EntityType.PACMAN:
            factory = self.pacman_modifier_factory
        odds, generator = self.rand.choice(factory, [odds for (odds, f) in factory])
        return generator()
