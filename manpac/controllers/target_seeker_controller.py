from manpac.utils import export
from manpac.direction import Direction
from manpac.entity_type import EntityType
from manpac.controllers.abstract_controller import AbstractController
from manpac.cell import Cell


import numpy as np


@export
class TargetSeekerController(AbstractController):
    """
    Reprents a target seeker controller.

    Parameters
    -----------
    - *game*: (**Game**)
        the game this controller is being used in
    """

    def __init__(self, game, aggro_refresh=5, path_refresh=20):
        super(TargetSeekerController, self).__init__(game)
        self.entity = None
        self.aggro = None
        self.path = []
        self.aggro_refresh = aggro_refresh
        self.path_refresh = path_refresh
        self._target = None
        self._dist_to_target = 0
        self._last_aggro_update = 9999
        self._last_path_update = 9999
        self.debug = False

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
            if not entity.alive or entity.type == EntityType.PACMAN:
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
        self.path, d = self.game.map.path_to(self.entity.map_position, self.game.map.closest_walkable(self.aggro.pos))
        self.on_change_path()

    def on_change_path(self):
        self._last_path_update = 0
        if self.path:
            self._make_new_target_(self.path[0])
        else:
            self._target = None
            self._dist_to_target = 1e9

    def _update_aggro_(self):
        old = self.aggro
        self.aggro = self.select_target()
        if not (old == self.aggro):
            self.on_change_target(old)
        else:
            # Compute new path
            self.path, d = self.game.map.path_to(self.entity.map_position, self.game.map.closest_walkable(self.aggro.pos))
            self.on_change_path()
        self._last_aggro_update = 0

    def _make_new_target_(self, target):
        self._target = target
        self._dist_to_target = np.linalg.norm(self.entity.map_position - target)

    def _on_reach_checkpoint_(self):
        self.path.pop(0)
        if self.path:
            self._make_new_target_(self.path[0])
        else:
            self._update_aggro_()

    def update(self, ticks):
        self._last_aggro_update += ticks
        self._last_path_update += ticks
        # Update target
        if self.aggro is None or not self.aggro.alive or self._last_aggro_update >= self.aggro_refresh:
            self._update_aggro_()

        # If no target location then go refresh aggro
        if self._target is None:
            self._last_aggro_update = self.aggro_refresh
            return

        # Update path if it's time
        if not self.path or self._last_path_update >= self.path_refresh:
            self.path, d = self.game.map.path_to(self.entity.map_position, self.game.map.closest_walkable(self.aggro.pos))
            self.on_change_path()

        if self.debug:
            for pt in self.path[:-1]:
                self.game.map[pt] = Cell.DEBUG_ONCE

        # Check if reached checkpoint
        if self._dist_to_target <= 0:
            if self.path:
                self._on_reach_checkpoint_()
            else:
                self._update_aggro_()
        # Check if we can reach the checkpoint
        self.entity.moving = True
        speed = self.entity.speed
        distance_done = self.game.map.how_far(self.entity, ticks * speed)
        if distance_done <= speed * .1:
            # Unblock -> center by going in the orthogonal direction
            directions = Direction.representing(self.entity.map_position + .5 - self.entity.pos)
            directions = [d for d in directions if d != -self.entity.direction]
            ticks_used = 1
            while directions and ticks > 0 and ticks_used > .01:
                self.entity.face(directions[0])
                ticks_used = self.game.map.move(self.entity, ticks) / speed
                ticks -= ticks_used
                directions = Direction.representing(self.entity.map_position + .5 - self.entity.pos)

            self.path, d = self.game.map.path_to(self.entity.map_position, self.game.map.closest_walkable(self.aggro.pos))
            self.on_change_path()

        # If we can reach checkpoint do it
        if distance_done > self._dist_to_target:
            ticks_used = self._dist_to_target / speed
            self.game.map.move(self.entity, ticks_used)
            ticks -= ticks_used
            self._on_reach_checkpoint_()

        # Face right direction
        self.entity.moving = bool(self.path)
        if self._target is not None:
            directions = Direction.representing(self._target - self.entity.map_position)
            if directions:
                self.entity.face(directions[0])

        distance_moved = self.game.map.move(self.entity, ticks)
        self._dist_to_target -= distance_moved
