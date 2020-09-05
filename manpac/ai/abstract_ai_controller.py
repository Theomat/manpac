from manpac.controllers.abstract_controller import AbstractController
from manpac.utils import export

from abc import ABC, abstractmethod


@export
class AbstractAIController(AbstractController, ABC):
    """
    An abstract AI controller to easily use with a model.
    """
    @abstractmethod
    def init_state(self):
        """
        Fired just before the game starts.
        """
        pass

    def on_game_start(self):
        self.init_state()

    @abstractmethod
    def get_action(self, ticks):
        """
        Obtain the action designed by this AI.
        Parameters
        -----------
        - *ticks*: (**float**)
            the maximum ticks that can be used

        Return
        -----------
        A tuple containing the direction in which to move, the number of ticks to use,
         and a boolean indicating if the modifier should be used.
        type: **Tuple[Direction, float, bool]**
        """
        pass

    def update(self, ticks):
        ticks_used = 1
        while ticks > 0 or ticks_used > .05:
            direction, ticks_used, boost_use = self.get_action(ticks)
            if boost_use:
                self.entity.use_modifier()
            self.entity.face(direction)
            if ticks_used > ticks:
                ticks_used = ticks
            self.entity.moving = ticks_used > .05
            self.game.map.move(self.entity, ticks_used)
            ticks -= ticks_used
