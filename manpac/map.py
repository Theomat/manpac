from manpac.utils import export
from manpac.entity_type import EntityType
from manpac.cell import Cell
from manpac.direction import Direction
from queue import PriorityQueue


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
        return considered_pos, True
    return unwalkable, False


def __find_first_walkable__(map, considered_pos, size, speed, v, ticks):
    unwalkables, timeout = __find_first_unwalkable__(map, considered_pos, speed, v, ticks)
    for unwalkable in unwalkables:
        walkable = unwalkable.astype(dtype=np.float)
        if not timeout:
            walkable -= v * 1       # Go back one case as it unwalkable
            walkable += .5          # Center position
            walkable += v * (.5 - size)  # Center relative to entity size
        yield walkable
    return []


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
        self.path_buffer = np.zeros_like(self.terrain, dtype=np.bool)
        self.max_bounds = np.array(shape) - 1
        # Boost generator
        self.boost_generator = boost_generator
        # Ghost boosts which are (loc, remaining_duration)
        self.ghost_boosts = []
        # Pacman boosts which are (loc, *)
        self.pacman_boosts = []
        # Boost livetime in ticks
        self.boost_duration = 600
        # Grab size distance of boost
        self.boost_size = .1

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
            for loc in new_boosts:
                self.ghost_boosts.append([loc, self.boost_duration])

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

    def closest_walkable(self, src):
        """
        Find the closest walkable cell from src.

        Parameters
        -----------
        - *src*: (**numpy.ndarray**)
            the source position

        Return
        -----------
        The closest walkable cell from src.
        type: **numpy.ndarray**
        """
        closest = None
        distance = 1e10

        considered_pos = [np.round(src)]
        while closest is None:
            new_considered_pos = []
            for pos in considered_pos:
                if not self.is_walkable(pos.astype(dtype=np.int)):
                    for direction in Direction:
                        new_considered_pos.append(pos + direction.vector)
                else:
                    dist = np.sum(np.square(src - pos))
                    if dist < distance:
                        distance = dist
                        closest = pos
            considered_pos = new_considered_pos
        return closest

    def spawn_entities(self, *entities):
        """
        Spawn the specified entities on this map.

        Parameters
        -----------
        - *entities*: (**Entity list**)
            the entities to be spawned on this map
        """
        for entity in entities:
            spawn = self.spawns[entity.type]
            if spawn.dtype == np.int:
                spawn = spawn.astype(dtype=np.float) + .5
            entity.teleport(spawn)

    def _heuristic_(self, abs_dist, distance_traveled):
        return abs_dist * 2 + distance_traveled

    def path_to(self, src, dst):
        """
        Find a list of walkable tiles from src to dst.
        Only returns the tiles where a direction change is needed.

        Parameters
        -----------
        - *src*: (**numpy.ndarray**)
            the source position
        - *dst*: (**numpy.ndarray**)
            the destination position, it must be walkable

        Return
        -----------
        False if no path exists.
        A list of tiles that needs to be reached where a direction change occurs if a path exists.
        type: **numpy.ndarray list**
        """
        src = src.astype(dtype=np.int)
        dst = dst.astype(dtype=np.int)
        d = np.sum(np.abs(dst - src))
        if not self.is_walkable(dst):
            return False
        if d == 0:
            return []
        self.path_buffer[:, :] = False
        paths = PriorityQueue()
        # (remaining_distance, dist_done, path_num, last_direction, checkpoints_list, last_position)
        paths.put([d, 0, 0, None, [], src, False])
        path_number = 0  # Used to avoid bug and to define an ordering
        while not paths.empty():
            score, dist_done, path_num, last_dir, pts, last_pos, flagged_pt = paths.get()
            for direction in Direction:
                new_cell = last_pos + direction.vector
                # if already walked skip
                if self.path_buffer[new_cell[0], new_cell[1]]:
                    continue
                # if not walkable skip
                if not self.is_walkable(new_cell):
                    continue
                self.path_buffer[new_cell[0], new_cell[1]] = True
                # If we change direction
                if last_dir != direction and last_dir is not None:
                    new_pts = pts[:]
                    new_pts.append(last_pos)
                    pts = new_pts
                new_score = np.sum(np.abs(dst - new_cell))
                if new_score == 0:
                    pts.append(dst)
                    return pts
                path_number += 1
                paths.put((self._heuristic_(new_score, dist_done + 1), dist_done, path_number, direction, pts, new_cell, False))
        return False

    def how_far(self, entity, max_distance):
        """
        Return how far the specified entity can move in their current direction.

        Parameters
        -----------
        - *entity*: (**Entity**)
            the entity to be considered
        - *max_distance*: (**float**)
            the maximum distance to be considered

        Return
        ----------
        The maximum distance the specified entity can continue in their direction before being blocked.
        type: **float**
        """
        speed = entity.speed
        if speed <= 0:
            return 0
        v = entity.direction.vector
        intangible = not entity.is_tangible
        maxi = 0
        if intangible:
            next = np.clip(entity.pos + v * (max_distance + entity.size), 0, self.max_bounds)
            maxi = min(np.max(np.abs(next - entity.pos)) / speed, max_distance)
        else:
            # Finds first unwalkable tile
            cases_where_entity = []
            for direction in Direction:
                position = entity.pos + direction.vector * entity.size * .99
                coord = position.astype(dtype=np.int)
                cases_where_entity.append(coord)
            walkables = __find_first_walkable__(self, cases_where_entity, entity.size, 1, v, max_distance)
            # Now walkable is target coordinates
            maxi = -1
            for walkable in walkables:
                diff = np.max((walkable - entity.pos) * v)
                if diff > 0:
                    if maxi < 0:
                        maxi = max_distance
                    maxi = min(diff, maxi)
            if maxi < 0:
                maxi = 0
        return maxi

    def move(self, entity, ticks):
        """
        Move the specified entity on this map for the specified number of ticks.

        Parameters
        -----------
        - *entity*: (**Entity**)
            the entity to be moved
        - *ticks*: (**float**)
            the number of ticks elapsed

        Return
        -----------
        The distance moved in the direction.
        type: **float**
        """
        speed = entity.speed
        if speed <= 0:
            return 0
        max_distance = self.how_far(entity, ticks * speed)
        maxi = max_distance / speed
        v = entity.direction.vector
        v_orth = entity.direction.rot90(1).vector

        # Pick up boosts
        boosts = self.ghost_boosts if entity.type is EntityType.GHOST else self.pacman_boosts
        for index, (loc, t) in enumerate(boosts):
            vector = (loc + .5) - entity.pos
            # if not in the right direction
            if (np.sign(vector) != v).all():
                continue
            # If on the side direction entity is not big enough to walk on it
            if np.max(np.abs(vector * v_orth)) > entity.size + self.boost_size:
                continue
            distance = np.max(vector * v) - entity.size - self.boost_size
            if distance <= maxi * speed:
                if self.boost_generator:
                    modifier = self.boost_generator.make_modifier(entity, loc)
                    entity.pickup(modifier)
                boosts.pop(index)
                if entity.type is EntityType.GHOST:
                    self.pacman_boosts.append([loc, t])
        # Actual movement
        entity.move(maxi)
        return maxi * speed

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
