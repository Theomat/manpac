from manpac.utils import export
from manpac.game_status import GameStatus
from manpac.entity_type import EntityType

import numpy as np


MAX_TICK_UNIT = 1


@export
class Game():
    """
    Represents a game comprised of the specified entities.

    Parameters
    -----------
    - *entities*: (**Entity iterable**)
        the collection of entities taking part in this game
    """

    def __init__(self, *entities):
        self.entities = list(entities)
        self.status = GameStatus.NOT_STARTED
        self.duration = 0

    def start(self, map):
        """
        Start a game on the specified map.

        Parameters
        -----------
        - *map*: (**Map**)
            the map this game will take place on
        """
        assert self.status is GameStatus.NOT_STARTED
        self.map = map
        self.duration = 0
        self.ghosts = 0
        for entity in self.entities:
            # Teleport entities at spawn points
            entity.teleport(self.map.spawns[entity.type])
            # Make them alive
            entity.alive = True
            # Count ghosts
            if entity.type is EntityType.GHOST:
                self.ghosts += 1
        # Update status
        self.status = GameStatus.ONGOING if self.ghosts > 1 else GameStatus.FINISHED

    def update(self, ticks):
        """
        Update this game for the specified number of ticks.

        Parameters
        -----------
        - *ticks*: (**float**)
            the number of ticks elapsed
        """
        assert self.status is GameStatus.ONGOING
        self.duration += ticks

        while ticks > MAX_TICK_UNIT and self.status is GameStatus.ONGOING:
            self.update(MAX_TICK_UNIT)
            ticks -= MAX_TICK_UNIT
        # Move entities
        self._move_entities_(ticks)
        # Update entities
        for entity in self.entities:
            entity.update(ticks)
        # Update map
        self.map.update(ticks)
        # Check collision
        self._check_collisions_()
        # Update status
        if self.ghosts <= 1:
            self.status = GameStatus.FINISHED

    def _move_entities_(self, ticks):
        # Move entities
        for entity in self.entities:
            self.map.move(entity, ticks)

    def _check_collisions_(self):
        cpy = self.entities[:]
        for i, entity1 in enumerate(cpy):
            for entity2 in cpy[i+1:]:
                can_collide = entity1.can_collide_with(entity2) or entity2.can_collide_with(entity1)
                if can_collide and \
                        entity1.squared_distance_to(entity2.pos) < (entity2.size + entity1.size)**2:
                    self.on_collision(entity1, entity2)
                    if not entity1.alive:
                        break

    def on_collision(self, entity1, entity2):
        """
        Procees to do the resolution of a collision between the two entities.
        Parameters
        -----------
        - *entity1*, *entity2*: (**Entity**)
            the entities that were part of the collision
        """
        if entity1.type is EntityType.PACMAN and entity2.type is EntityType.GHOST:
            entity2.kill()
            self.entities.remove(entity2)
            self.ghosts -= 1
        elif entity2.type is EntityType.PACMAN and entity1.type is EntityType.GHOST:
            self.on_collision(entity2, entity1)
        else:
            v1 = entity1.speed * entity1.direction.vector
            v2 = entity2.speed * entity2.direction.vector
            distance = np.linalg.norm(v1) + np.linalg.norm(v2)
            to_spread = entity1.distance_to(entity2.pos) - (entity2.size + entity1.size)
            coeff = to_spread / distance
            entity1.teleport(entity1.pos + v1 * coeff)
            entity2.teleport(entity2.pos + v2 * coeff)
