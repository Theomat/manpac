from manpac.utils import export

from abc import ABC


@export
class AbstractController(ABC):
    """
    Reprents an abstract controller.
    """

    def __init__(self, game):
        self.game = game
        self.entity = None

    def on_attach(self, entity):
        self.entity = entity

    def on_death(self):
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
