from manpac.utils import export
from manpac.entity_type import EntityType
from manpac.cell import Cell

import numpy as np


def __next_cell__(pos, max_bounds, v, speed, ticks):
    next = np.clip(pos + v, 0, max_bounds)
    ticks_used = min(np.max(np.abs(next - pos)) / speed, ticks)
    return next.astype(dtype=np.int), ticks_used


@export
class Map():
    """
    Represents a map.
    """

    def __init__(self, shape):
        # Init spawn points
        self.spawns = {}
        for type in EntityType:
            self.spawns[type] = np.zeros((2,))
        # The actual terrain
        self.terrain = np.full(shape, Cell.EMPTY)
        self.max_bounds = np.array(shape) - 1
        # Boost generator
        self.boost_generator = None
        # Ghost boosts
        self.ghost_boosts = []
        # Pacman boosts
        self.pacman_boosts = []
        # Boost livetime
        self.boost_duration = 600

    def update(self, ticks):
        """
        Update this map for the specified number of ticks.

        Parameters
        -----------
        - *ticks*: (**float**)
            the number of ticks elapsed
        """
        new_boosts = []
        for boost in self.ghost_boosts:
            loc, ticks_remaining = boost
            # Spawn pacman boost
            if ticks_remaining <= ticks:
                self.pacman_boosts.append(boost)
            else:
                boost[1] -= ticks
                new_boosts.append(boost)
        self.ghost_boosts = new_boosts
        # Add new boosts
        if self.boost_generator:
            new_boosts = self.boost_generator.generate(ticks)
            for boost in new_boosts:
                self.ghost_boosts.append([boost, self.boost_duration])

    def __getitem__(self, key):
        if isinstance(key, np.ndarray):
            return self.terrain[key[0], key[1]]
        else:
            return self.terrain[key]

    def __setitem__(self, key, value):
        if isinstance(key, np.ndarray):
            self.terrain[key[0], key[1]] = value
        else:
            self.terrain[key] = value

    def is_walkable(self, pos):
        return Cell(self[pos]).walkable

    def move(self, entity, ticks):
        """
        Move the specified entity on this map for the specified number of ticks.
        """
        speed = entity.speed
        if speed <= 0:
            return
        v = entity.direction.vector.astype(dtype=np.int)
        intangible = not entity.is_tangible
        maxi = 0
        if intangible:
            next = np.clip(entity.pos + v * (ticks + entity.size), 0, self.max_bounds)
            maxi = min(np.max(np.abs(next - entity.pos)) / speed, ticks)
        else:
            # Finds first unwalkable tile
            current = entity.pos.copy()
            times = 0
            while (current <= self.max_bounds).all() and \
                    (current >= 0).all() and \
                    self.is_walkable(current.astype(dtype=np.int)) and \
                    times - 1 < speed * ticks:
                current += v
                times += 1
            # Now current is unwalkable
            walkable = np.clip(current, entity.size, self.max_bounds - entity.size)
            if not self.is_walkable(walkable.astype(dtype=np.int)):
                to_out = walkable - walkable.astype(dtype=np.int)
                walkable -= v * (to_out + entity.size)
            # Now walkable is target coordinates
            maxi = min(np.max(np.abs(walkable - entity.pos)) / speed, ticks)
        # Pick up boosts
        boosts = self.ghost_boosts if entity.type is EntityType.GHOST else self.pacman_boosts
        for index, (loc, t) in enumerate(boosts):
            coeff = loc - entity.pos
            if (np.sign(coeff) != np.sign(v)).any():
                continue
            coeff = np.max(entity.size + np.abs(coeff))
            if coeff <= maxi:
                if self.boost_generator:
                    modifier = self.boost_generator.make_modifier(entity, loc)
                    entity.pickup(modifier)
                boosts.pop(index)
                if entity.type is EntityType.GHOST:
                    self.pacman_boosts.append([loc, t])
        # Actual movement
        entity.move(maxi)
