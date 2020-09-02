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
        min_square_dist = 50
        for pac in pacs:
            new_choices = []
            dif_pos = self.entity.pos - pac.pos
            square_dist = np.sum(abs(dif_pos))
            if square_dist < min_square_dist:
                min_square_dist = square_dist
                closest_pac = pac
            for direction in choices:
                if np.max(direction.vector * dif_pos) > 0:
                    new_choices.append(direction)
            choices = new_choices

        len_choices = len(choices)
        if len_choices == 0:
            choices = [dir for dir in Direction
                       if self.game.map.is_walkable(self.entity.map_position + dir.vector)]
            dif_pos = self.entity.pos - closest_pac.pos
            dif_pos[np.argmax(abs(dif_pos))] = 0
            for direction in choices:
                if np.max(direction.vector * dif_pos) > 0:
                    return [direction]
            return []
        elif len_choices == 1:
            return [choices[0]]
        else:
            return [random.choice(choices)]


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

        self.game.map.move(self.entity, ticks)
