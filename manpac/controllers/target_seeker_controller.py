from manpac.utils import export
from manpac.direction import Direction
from manpac.entity_type import EntityType
from manpac.controllers.abstract_controller import AbstractController


from queue import PriorityQueue
import numpy as np


AGGRO_REFRESH = 1
PATH_REFRESH = 1


def find_path(src, dst, map):
    d = np.sum(np.abs(dst - src))
    if d == 0:
        return []

    paths = PriorityQueue()
    paths.put([d, 0, [], src])
    while not paths.empty():
        score, len, path, current = paths.get()
        for direction in Direction:
            new_path = path[:]
            new_cell = current + direction.vector
            # if not walkable skip
            if not map.is_walkable(new_cell):
                continue
            new_path.append(direction)
            new_score = np.sum(np.abs(dst - new_cell))
            if new_score == 0:
                return new_path
            paths.put((new_score, len + 1, new_path, new_cell))
    return []


@export
class TargetSeekerController(AbstractController):
    """
    Reprents a target seeker controller.

    Parameters
    -----------
    - *game*: (**Game**)
        the game this controller is being used in
    """

    def __init__(self, game):
        super(TargetSeekerController, self).__init__(game)
        self.entity = None
        self.aggro = None
        self.path = []
        self._last_aggro_update = 9999
        self._last_path_update = 9999

    def select_target(self):
        """
        Select the new target.

        Return
        ----------
        The new entity to target.
        type: (**Entity**)
        """
        closest = self.aggro
        distance = 1e14
        for entity in self.game.entities:
            if entity.type == EntityType.PACMAN:
                continue
            d = self.entity.squared_distance_to(entity.pos)
            if d < distance:
                distance = d
                closest = entity
        return closest

    def on_change_target(self, old_target):
        """
        Fired upon change of target.

        Parameters
        -----------
        - *old_target*: (**Entity**)
            the old target
        """
        self._last_path_update = 0
        self.path = find_path(self.entity.map_position, self.game.map.closest_walkable(self.aggro.pos), self.game.map)

    def update(self, ticks):
        self._last_aggro_update += ticks
        self._last_path_update += ticks
        # Update target
        if self._last_aggro_update >= AGGRO_REFRESH:
            old = self.aggro
            self.aggro = self.select_target()
            if not (old == self.aggro):
                self.on_change_target(old)
            self._last_aggro_update = 0

        # Update path
        if self._last_path_update >= PATH_REFRESH:
            self.path = find_path(self.entity.map_position, self.game.map.closest_walkable(self.aggro.pos), self.game.map)
            self._last_path_update = 0

        # Face right direction
        self.entity.moving = True
        if self.path:
            self.entity.face(self.path[0])
