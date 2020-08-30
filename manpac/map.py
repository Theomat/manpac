from manpac.utils import export
from manpac.entity_type import EntityType
from manpac.cell import Cell
from manpac.direction import Direction

import numpy as np


def __find_first_unwalkable__(map, considered_pos, speed, v, ticks):
    times = 0
    unwalkable = [pos for pos in considered_pos if not map.is_walkable(pos.astype(dtype=np.int))]
    while not unwalkable and times - 1 < speed * ticks:
        for pos in considered_pos:
            pos += v
        unwalkable = [pos for pos in considered_pos if not map.is_walkable(pos.astype(dtype=np.int))]
        times += 1
    # Not enough time
    if times - 1 >= speed * ticks:
        return considered_pos
    return unwalkable

def __find_first_walkable__(map, considered_pos, size, speed, v, ticks):
    unwalkables = __find_first_unwalkable__(map, considered_pos, speed, v, ticks)
    for unwalkable in unwalkables:
        walkable = np.clip(unwalkable, size, map.max_bounds - size)
        if not map.is_walkable(walkable.astype(dtype=np.int)):
            to_out = np.abs(walkable - walkable.astype(dtype=np.int))
            walkable -= v * (to_out + size)
        yield walkable


@export
class Map():
    """
    Represents a map.

    Parameters
    -----------
    - *shape*: (**array_like**)
        the shape of the map
    - *boost_generator* (**AbstractBoostGenerator**)
        the boost generator of this map
    """

    def __init__(self, shape, boost_generator=None):
        # Init spawn points
        self.spawns = {}
        for type in EntityType:
            self.spawns[type] = np.zeros((2,))
        # The actual terrain
        self.terrain = np.full(shape, Cell.EMPTY)
        self.max_bounds = np.array(shape) - 1
        # Boost generator
        self.boost_generator = None
        # Ghost boosts which are (loc, remaining_duration)
        self.ghost_boosts = []
        # Pacman boosts which are (loc, *)
        self.pacman_boosts = []
        # Boost livetime
        self.boost_duration = 600

    @property
    def width(self):
        """
        The width of this map.
        type: **int**
        """
        return self.terrain.shape[0]

    @property
    def height(self):
        """
        The height of this map.
        type: **int**
        """
        return self.terrain.shape[1]

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
        """
        Return True is the specified pos is within bounds and walkable.

        Parameters
        -----------
        - *pos*: (**numpy.ndarray**)
            the position to look at
        Return
        -----------
        True is the specified pos is within bounds and walkable.
        type: **bool**
        """
        if (pos < 0).any() or (pos > self.max_bounds).any():
            return False
        return Cell(self[pos]).walkable

    def closest_walkable(self, pos):
        """
        """
        closest = None
        distance = 1e10

        considered_pos = [pos.astype(dtype=np.int)]
        while closest is None:
            new_considered_pos = []
            for pos in considered_pos:
                for direction in Direction:
                    new_pos = pos + direction.vector
                    if not self.is_walkable(new_pos):
                        new_considered_pos.append(new_pos)
                    else:
                        dist = np.sum(np.square(pos - new_pos))
                        if dist < distance:
                            distance = dist
                            closest = new_pos
            considered_pos = new_considered_pos
        return closest

    def move(self, entity, ticks):
        """
        Move the specified entity on this map for the specified number of ticks.

        Parameters
        -----------
        - *entity*: (**Entity**)
            the entity to be moved
        - *ticks*: (**float**)
            the number of ticks elapsed
        """
        speed = entity.speed
        if speed <= 0:
            return
        v = entity.direction.vector
        intangible = not entity.is_tangible
        maxi = 0
        if intangible:
            next = np.clip(entity.pos + v * (ticks + entity.size), 0, self.max_bounds)
            maxi = min(np.max(np.abs(next - entity.pos)) / speed, ticks)
        else:
            # Finds first unwalkable tile
            cases_where_entity = []
            for direction in Direction:
                coord = self.closest_walkable(entity.pos + direction.vector)
                if entity.squared_distance_to(coord) <= entity.size**2:
                    cases_where_entity.append(coord)
            walkables = __find_first_walkable__(self, cases_where_entity, entity.size, speed, v, ticks)

            # Now walkable is target coordinates
            maxi = ticks if walkables else 0
            for walkable in walkables:
                maxi = min(np.max(np.abs(walkable - entity.pos)) / speed, maxi)

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

    def print(self, empty=" ", wall="O"):
        """
        Print this map to the standard output stream.

        Parameters
        -----------
        - *empty*: (**string**)
            the string used to represent en empty cell
        - *wall*: (**string**)
            the string used to represent a wall cell
        """
        for y in range(self.height):
            for x in range(self.width):
                if self[x, y] == Cell.EMPTY:
                    print(empty, end="")
                else:
                    print(wall, end="")
            print("")
