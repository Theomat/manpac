from manpac.utils import export
from manpac.direction import Direction
from manpac.controllers.abstract_controller import AbstractController

import random


@export
class RandomWalkController(AbstractController):
    """
    Reprents a random walk controller.

    Parameters
    -----------
    - *game*: (**Game**)
        the game this controller is being used in
    - *switch_duration*: (**float**)
        the number of ticks before it changes direction
    """

    def __init__(self, game, switch_duration):
        super(RandomWalkController, self).__init__(game)
        self._dir_duration = switch_duration + 1
        self.switch_duration = switch_duration

    def update(self, ticks):
        self._dir_duration += ticks
        # If can not move in that direction anymore, indicate to change direction
        if not self.game.map.is_walkable(self.entity.map_position + self.entity.direction.vector):
            self._dir_duration = self.switch_duration + 1
        # Change direction after some time
        if self._dir_duration > self.switch_duration:
            choices = [dir for dir in Direction
                       if self.game.map.is_walkable(self.entity.map_position + dir.vector)]
            if choices:
                self.entity.face(random.choice(choices))
            self.entity.moving = True
            self._dir_duration = 0
