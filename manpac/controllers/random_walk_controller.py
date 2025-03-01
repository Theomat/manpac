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

    def __init__(self, game, switch_duration=60):
        super(RandomWalkController, self).__init__(game)
        self._dir_duration = switch_duration + 1
        self.switch_duration = switch_duration

    def update(self, ticks):
        self._dir_duration += ticks
        # Change direction after some time
        if self._dir_duration > self.switch_duration:
            choices = [dir for dir in Direction
                       if self.game.map.is_walkable(self.entity.map_position + dir.vector)]
            if choices:
                self.entity.face(random.choice(choices))
            self.entity.moving = True
            self._dir_duration = 0
        else:
            speed = self.entity.speed
            used_ticks = self.game.map.how_far(self.entity, speed * ticks) / speed
            self.game.map.move(self.entity, used_ticks)
            if used_ticks < ticks:
                # Force direction change
                self._dir_duration = self.switch_duration + 1
                self.update(ticks-used_ticks)
        self.entity.use_modifier()
