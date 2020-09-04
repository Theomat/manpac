from manpac.utils import export
from manpac.direction import Direction
from manpac.controllers.abstract_controller import AbstractController
from manpac.entity_type import EntityType

import random
import numpy as np


@export
class WalkAwayController(AbstractController):
    """
    Represents a random walk controller.

    Parameters
    -----------
    - *game*: (**Game**)
        the game this controller is being used in
    - *switch_duration*: (**float**)
        the number of ticks before it changes direction
    """

    def __init__(self, game, switch_duration):
        super(WalkAwayController, self).__init__(game)
        self._dir_duration = switch_duration + 1
        self.switch_duration = switch_duration

    def _get_dir_away_(self):
        pacs = [entity for entity in self.game.entities if entity.type == EntityType.PACMAN]
        choices = [dir for dir in Direction
                   if self.game.map.is_walkable(self.entity.map_position + dir.vector)]
        max_min_square_dist = 0
        for direction in choices:
            per_dir_min = 50
            for pac in pacs:
                test_path = self.game.map.path_to(pac.pos, self.entity.map_position + direction.vector)
                tmp_dist = 0
                for i in range(len(test_path)-1):
                    tmp_dist += np.sum(np.abs(test_path[i+1] - test_path[i]))
                if tmp_dist < per_dir_min:
                    per_dir_min = tmp_dist
            if per_dir_min > max_min_square_dist:
                max_min_square_dist = per_dir_min
                return_dir = direction

        if max_min_square_dist == 0:
            print("no dir")
            return []
        print(return_dir)
        return [return_dir]



    def update(self, ticks):
        self._dir_duration += ticks
        # If can not move in that direction anymore, indicate to change direction
        if self.entity.moving and self.game.map.how_far(self.entity, 1) < self.entity.size:
            self._dir_duration = self.switch_duration + 1
        # Change direction after some time
        if self._dir_duration > self.switch_duration:
            choice = self._get_dir_away_()
            if choice:
                self.entity.face(choice[0])
                self.entity.moving = True
            else:
                self.entity.moving = False
            self._dir_duration = 0
        else:
            self.entity.moving = True
            speed = self.entity.speed
            used_ticks = self.game.map.how_far(self.entity, speed * ticks) / speed
            self.game.map.move(self.entity, used_ticks)
            if used_ticks < ticks:
                # Force direction change
                self._dir_duration = self.switch_duration + 1
                self.update(ticks - used_ticks)

        self.entity.use_modifier()
