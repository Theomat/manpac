from manpac.utils import export
from manpac.direction import Direction
from manpac.entity_type import EntityType

import numpy as np
import operator
from functools import reduce


@export
class Entity():
    """
    Represents a game entity.

    Parameters
    -----------
    - *type*: (**EntityType**)
        the type of this entity
    """

    def __init__(self, type):
        # The current coordinates of the center of this entity
        self.pos = np.zeros((2,), dtype=np.float64)
        # True if the entity is alive otherwise False
        self.alive = False
        # Default speed in cells / tick
        self.base_speed = .2
        if type is EntityType.PACMAN:
            self.base_speed *= 1.2
        # Their size (radius) in cells
        self.size = .35
        # True if entity is moving otherwise False
        self.moving = False
        # Their current facing direction
        self.direction = Direction.LEFT
        # This entity type
        self.type = type
        # Holding modifier
        self.holding = None
        # List of current modifiers of the entity
        self.modifiers = []
        # Current controller of the entity
        self.controller = None

    def attach(self, controller):
        """
        Attach the specified controller to this entity.
        Parameters
        -----------
        - *controller*: (**AbstractController**)
            the controller to be attached
        """
        self.controller = controller
        if self.controller:
            controller.on_attach(self)

    @property
    def map_position(self):
        """
        The map position of this entity.
        type: **numpy.ndarray**, dtype=numpy.int
        """
        return np.floor(self.pos).astype(dtype=np.int)

    @property
    def speed(self):
        """
        The current speed of this entity in cells / tick.
        type: **float**
        """
        return reduce(operator.mul,
                      [modifier.speed_multiplier for modifier in self.modifiers],
                      self.base_speed * self.moving)

    def face(self, direction):
        """
        Change the direction of this entity to the new direction.
        Parameters
        -----------
        - *direction*: (**Direction**)
            the direction to face
        """
        self.direction = direction

    def squared_distance_to(self, pos):
        """
        Return the square of the distance from this entity towards the specified position.
        Parameters
        -----------
        - *pos*: (**numpy.ndarray**)
            the position to compute the distance to

        Return
        -----------
        The square of the distance between this entity's position and the specified position.
        type: **float**
        """
        return np.sum(np.square(self.pos - pos))

    def distance_to(self, pos):
        """
        Return the distance from this entity towards the specified position.
        Parameters
        -----------
        - *pos*: (**numpy.ndarray**)
            the position to compute the distance to

        Return
        -----------
        The distance between this entity's position and the specified position.
        type: **float**
        """
        return np.linalg.norm(self.pos - pos)

    def move(self, ticks):
        """
        Moves this entity for the specified number of ticks.

        Parameters
        -----------
        - *ticks*: (**float**)
            the number of ticks elapsed
        """
        if not self.alive:
            return
        self.pos += self.direction.vector * self.speed * ticks

    def teleport(self, pos):
        """
        Teleport this entity to the specified position.
        Parameters
        -----------
        - *pos*: (**numpy.ndarray**)
            the position to teleport to
        """
        self.pos[:] = pos[:]

    def update(self, ticks):
        """
        Update this entity for the specified number of ticks.

        Parameters
        -----------
        - *ticks*: (**float**)
            the number of ticks elapsed
        """
        if not self.alive:
            return
        new_modifiers = []
        dead_modifiers = []
        for modifier in self.modifiers:
            modifier.update(ticks)
            if modifier.alive:
                new_modifiers.append(modifier)
            else:
                dead_modifiers.append(modifier)

        self.modifiers = new_modifiers
        for modifier in dead_modifiers:
            modifier.on_death(self)
        if self.controller:
            self.controller.update(ticks)

    def pickup(self, modifier):
        """
        Pickup the specified modifier, if the entity is already holding a modifier, the former is discarded.

        Parameters
        -----------
        - *modifier*: (**AbstractModifier**)
            the modifier to be picked up
        """
        if not self.holding:
            self.holding = modifier
            if self.controller:
                self.controller.on_boost_pickup()
            modifier.on_pickup(self)

    def use_modifier(self):
        """
        Use the modifier this entity is holding.
        """
        if self.holding:
            self.modifiers.append(self.holding)
            if self.controller:
                self.controller.on_boost_use()
            self.holding.use(self)
            self.holding = None

    @property
    def is_tangible(self):
        """
        False if this entity can walk through walls or any entities.
        type: **bool**
        """
        return reduce(operator.and_,
                      [modifier.is_tangible for modifier in self.modifiers],
                      True)

    def can_collide_with(self, other):
        """
        Return True only if this entity can collide with the specified entity type.
        Parameters
        -----------
        - *other*: (**EntityType**)
            the entity type to check collision with
        Return
        -----------
        True if this entity can collide with the specified entity, False otherwise.
        type: **bool**
        """
        if self.type is EntityType.PACMAN or other is EntityType.PACMAN:
            return self.is_tangible
        else:
            return reduce(operator.or_,
                          [modifier.can_ghost_collide for modifier in self.modifiers],
                          False)

    def kill(self):
        """
        Kill this entity.
        """
        self.alive = False
        self.moving = False
        if self.controller:
            self.controller.on_death()
