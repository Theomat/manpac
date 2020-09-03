from manpac.entity_type import EntityType
from manpac.entity import Entity
from manpac.map import Map
from manpac.game import Game
from manpac.direction import Direction
from manpac.game_status import GameStatus
from manpac.controllers.target_seeker_controller import TargetSeekerController

import pytest
import numpy as np


def test_status():
    g = Game(Entity(EntityType.GHOST), Entity(EntityType.PACMAN))

    assert g.status is GameStatus.NOT_STARTED
    g.start(Map((10, 10)))
    assert g.status is GameStatus.FINISHED


def test_collision_resolution():
    ghost = Entity(EntityType.GHOST)
    pacman = Entity(EntityType.PACMAN)
    pacman.moving = True
    pacman2 = Entity(EntityType.PACMAN)
    pacman2.moving = True
    pacman2.face(-pacman.direction)

    map = Map((10, 10))
    map.spawns[EntityType.GHOST] = np.array([1, 1])
    map.spawns[EntityType.PACMAN] = np.array([1, 1])

    g = Game(ghost, pacman, pacman2)
    g.start(map)

    g.on_collision(pacman, ghost)
    assert not ghost.alive
    assert pacman.alive

    g.entities.append(ghost)
    ghost.alive = True
    g.on_collision(ghost, pacman)
    assert not ghost.alive
    assert pacman.alive

    assert pacman.squared_distance_to(pacman2.pos) < (pacman2.size + pacman.size)**2
    g.on_collision(pacman, pacman2)
    assert pacman.squared_distance_to(pacman2.pos) >= (pacman2.size + pacman.size)**2


@pytest.mark.timeout(5)
def test_big_updates():
    ghost = Entity(EntityType.GHOST)
    ghost2 = Entity(EntityType.GHOST)
    ghost3 = Entity(EntityType.GHOST)
    ghost4 = Entity(EntityType.GHOST)
    pacman = Entity(EntityType.PACMAN)
    ghost2.moving = False

    g = Game(ghost, pacman, ghost2, ghost3, ghost4)

    controller = TargetSeekerController(g)
    pacman.attach(controller)

    g.start(Map((10, 10)))
    ghost2.teleport(Direction.RIGHT.vector * 3)
    ghost3.teleport(Direction.DOWN.vector * 3)
    assert g.status is GameStatus.ONGOING
    g.update(1e12)
    assert g.status is GameStatus.FINISHED
