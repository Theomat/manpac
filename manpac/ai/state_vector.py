from manpac.utils import export
from manpac.entity_type import EntityType
from manpac.modifiers.ghost_block_modifier import GhostBlockModifier
from manpac.modifiers.intangible_modifier import IntangibleModifier
from manpac.modifiers.speed_modifier import SpeedModifier
from manpac.modifiers.swap_modifier import SwapModifier

import numpy as np


__SIZE_PER_ENTITY__ = 14


@export
def init_state_vector(game):
    """
    Allocates and init a state vector representing this game.
    Parameters
    -----------
    - *game*: (**Game**)
        the game the state vector will represent
    Return
    -----------
    A initialized state vector.
    type: **numpy.ndarray**
    """
    assert game.map is not None
    entities_size = len(game.entities) * __SIZE_PER_ENTITY__
    map_size = np.product(game.map.terrain.shape)
    state_vector = np.zeros((entities_size + map_size + 1), dtype=np.float)
    np.copyto(state_vector[entities_size:], np.flatten(game.map.terrain))
    return state_vector


def __push_entity_data__(entity, out):
    out[0] = entity.pos[0]
    out[1] = entity.pos[1]
    out[2] = entity.direction
    out[3] = entity.speed
    out[4:6] = entity.speed * entity.direction.vector
    out[7] = entity.is_tangible
    out[8] = entity.can_collide_with(EntityType.GHOST)
    out[9] = entity.can_collide_with(EntityType.PACMAN)
    out[10] = entity.type
    out[11] = entity.size
    out[12] = entity.alive
    if entity.holding:
        if isinstance(entity.holding, GhostBlockModifier):
            out[13] = 1
        elif isinstance(entity.holding, IntangibleModifier):
            out[13] = 2
        elif isinstance(entity.holding, SpeedModifier):
            out[13] = 3
        elif isinstance(entity.holding, SwapModifier):
            out[13] = 4
    else:
        out[13] = 0


@export
def update_state_vector(game, self, state_vector):
    """
    Update the state vector representing the game.
    Parameters
    -----------
    - *game*: (**Game**)
        the game the state vector will represent
    - *self*: (**Entity**)
        the entity point of view
    - *state_vector*: (**numpy.ndarray**)
        the old state vector
    """
    # Reset boost location of the map
    state_vector[state_vector >= 2] = 0
    # Push entity data
    index = 1
    __push_entity_data__(self, state_vector[index:])
    index += __SIZE_PER_ENTITY__
    for entity in game.entities:
        if self == entity:
            continue
        __push_entity_data__(entity, state_vector[index:])
        index += __SIZE_PER_ENTITY__
    # Push ghost boost location
    for (loc, r) in game.map.ghost_boosts:
        nindex = index + loc[0] * game.map.height + loc[1]
        state_vector[nindex] = 2
    # Push ghost boost location
    for (loc, r) in game.map.pacman_boosts:
        nindex = index + loc[0] * game.map.height + loc[1]
        state_vector[nindex] = 3
