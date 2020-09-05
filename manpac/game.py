from manpac.utils import export
from manpac.game_status import GameStatus
from manpac.entity_type import EntityType

import numpy as np


MAX_TICK_UNIT = .5


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
        map.reset()
        map.compile()
        self.map = map
        self.duration = 0
        self.ghosts = 0
        for entity in self.entities:
            # Make them alive
            entity.alive = True
            # Count ghosts
            if entity.type is EntityType.GHOST:
                self.ghosts += 1
        # Spawn entities
        self.map.spawn_entities(*self.entities)
        # Fire on_game_start event
        for entity in self.entities:
            if entity.controller:
                entity.controller.on_game_start()
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

    def _check_collisions_(self):
        cpy = self.entities[:]
        for i, entity1 in enumerate(cpy):
            if not entity1.alive:
                continue
            for entity2 in cpy[i+1:]:
                if not entity2.alive:
                    continue
                can_collide = entity1.can_collide_with(entity2.type) or entity2.can_collide_with(entity1.type)
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
            self.ghosts -= 1
        elif entity2.type is EntityType.PACMAN and entity1.type is EntityType.GHOST:
            self.on_collision(entity2, entity1)
        else:
            v1 = entity1.direction.vector
            v2 = entity2.direction.vector
            distance = np.linalg.norm(v1) + np.linalg.norm(v2)
            to_spread = entity1.distance_to(entity2.pos) - (entity2.size + entity1.size)
            coeff = 2 * to_spread / distance
            coeff1 = 1
            coeff2 = 1
            if entity1.can_collide_with(entity2):
                if not entity2.can_collide_with(entity1):
                    coeff1 = 0
            elif entity2.can_collide_with(entity1):
                coeff2 = 0

            coeff /= (coeff1 + coeff2)
            entity1.teleport(entity1.pos + v1 * coeff1 * coeff)
            entity2.teleport(entity2.pos + v2 * coeff2 * coeff)
            self.map.teleport_back_on_map(entity1)
            self.map.teleport_back_on_map(entity2)
