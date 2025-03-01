from manpac.entity_type import EntityType
from manpac.entity import Entity
from manpac.map import Map
from manpac.game import Game
from manpac.direction import Direction
from manpac.game_status import GameStatus
from manpac.controllers.target_seeker_controller import TargetSeekerController
from manpac.controllers.random_walk_controller import RandomWalkController

import pytest


@pytest.mark.timeout(3)
def test_static_hunt():
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
    assert g.ghosts == 4
    while g.status is GameStatus.ONGOING:
        g.update(1)
    assert g.status is GameStatus.FINISHED


@pytest.mark.timeout(5)
def test_random_hunt():
    ghost = Entity(EntityType.GHOST)
    ghost2 = Entity(EntityType.GHOST)
    ghost3 = Entity(EntityType.GHOST)
    ghost4 = Entity(EntityType.GHOST)
    pacman = Entity(EntityType.PACMAN)
    ghost2.moving = False

    g = Game(ghost, pacman, ghost2, ghost3, ghost4)
    for entity in g.entities:
        if entity.type is EntityType.GHOST:
            entity.attach(RandomWalkController(g, 2))

    controller = TargetSeekerController(g)
    pacman.attach(controller)

    g.start(Map((10, 10)))
    ghost2.teleport(Direction.RIGHT.vector * 3)
    ghost3.teleport(Direction.DOWN.vector * 3)
    assert g.status is GameStatus.ONGOING
    assert g.ghosts == 4
    while g.status is GameStatus.ONGOING:
        g.update(1)
    assert g.status is GameStatus.FINISHED
