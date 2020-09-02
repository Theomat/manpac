from manpac.utils import export
from manpac.entity_type import EntityType

from abc import ABC


@export
class AbstractModifier(ABC):
    """
    Represents an abstract modifier.

    Parameters
    -----------
    - *game*: (**Game**)
        the game this modifier is being used in
    - *duration*: (**float**)
        the number of ticks on use this modifier will last
    """

    def __init__(self, game, duration):
        self.game = game
        self.used = False
        # Remaining duration of the modifier in ticks
        self.remaining_duration = duration

    @property
    def speed_multiplier(self):
        """
        Speed multiplier conferred by this modifier.
        type: **float**
        """
        return 1

    @property
    def is_tangible(self):
        """
        Whether this modifier makes entities intangible (i.e. can walk through wall) or not.
        type: **bool**
        """
        return True

    @property
    def can_ghost_collide(self):
        """
        Whether this modifier makes a ghost able to collide with other ghosts.
        type: **bool**
        """
        return False

    @property
    def alive(self):
        """
        Whether this modifier is active or not.
        type: **bool**
        """
        return not self.used or self.remaining_duration > 0

    def use(self, entity):
        """
        Use this modifier on the specified entity.

        Parameters
        -----------
        - *entity*: (**Entity**)
            the entity this modifier is being used on
        """
        self.used = True
        self.on_use(entity)

    def on_use(self, entity):
        """
        Fired when this modifier is used on an entity.

        Parameters
        -----------
        - *entity*: (**Entity**)
            the entity this modifier is being used on
        """
        pass

    def on_death(self, entity):
        """
        Fired when this modifier is removed from an entity.

        Parameters
        -----------
        - *game*: (**Game**)
            the game it was used in
        - *entity*: (**Entity**)
            the entity this modifier was used on
        """
        pass

    def on_pickup(self, entity):
        if entity.type is EntityType.PACMAN:
            entity.use_modifier()

    def update(self, ticks):
        """
        Update this entity for the specified number of ticks.

        Parameters
        -----------
        - *ticks*: (**float**)
            the number of ticks elapsed
        """
        if self.used:
            self.remaining_duration -= ticks
