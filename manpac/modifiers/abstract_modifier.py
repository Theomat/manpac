from manpac.utils import export

from abc import ABC


@export
class AbstractModifier(ABC):
    """
    Represents an abstract modifier.
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
        """
        return 1

    @property
    def is_tangible(self):
        """
        Whether this modifier makes this entity intangible (i.e. can walk through wall) or not.
        """
        return True

    @property
    def can_ghost_collide(self):
        """
        Whether this modifier makes this ghost able to collide with other ghosts.
        """
        return False

    @property
    def alive(self):
        """
        Whether this modifier is alive or not.
        """
        return not self.used or self.remaining_duration > 0

    def use(self, entity):
        self.used = True
        self.on_use(entity)

    def on_use(self, entity):
        """
        Fired when this modifier is used on entity.

        Parameters
        -----------
        - *game*: (**Game**)
            the game it is being used in
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
        pass

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
