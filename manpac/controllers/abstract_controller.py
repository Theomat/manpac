from manpac.utils import export

from abc import ABC


@export
class AbstractController(ABC):
    """
    Represents an abstract controller.

    Parameters
    -----------
    - *game*: (**Game**)
        the game this controller is being used in
    """

    def __init__(self, game):
        self.game = game
        self.entity = None

    def on_attach(self, entity):
        """
        Fired when this controller is attached to an entity.

        Parameters
        -----------
        - *entity*: (**Entity**)
            the entity this controller is being attached to
        """
        self.entity = entity

    def on_game_start(self):
        """
        Fired before the game starts, after entities have spawned.
        """
        pass

    def on_game_end(self):
        """
        Fired when the game ends.
        """
        pass

    def on_boost_pickup(self):
        """
        Fired just after a boost is picked up.
        """
        pass

    def on_boost_use(self):
        """
        Fired just before a boost is used.
        """
        pass

    def on_death(self):
        """
        Fired upon the death of the entity this controlled was attached to.
        """
        pass

    def update(self, ticks):
        """
        Update this controller for the specified number of ticks.

        Parameters
        -----------
        - *ticks*: (**float**)
            the number of ticks elapsed
        """
        pass
