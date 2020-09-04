from manpac.entity_type import EntityType
from manpac.entity import Entity
from manpac.direction import Direction


import numpy as np


def test_distance():
    a = Entity(EntityType.GHOST)

    p1 = np.random.random_sample(2) * 1000
    d1 = a.distance_to(p1)

    for i in range(10):
        pos = np.random.random_sample(2) * 1000
        assert a.distance_to(pos) >= 0
        assert a.distance_to(pos) + d1 >= a.distance_to(pos + p1)


def test_squared_distance():
    a = Entity(EntityType.GHOST)
    for i in range(10):
        pos = np.random.random_sample(2) * 1000
        d = a.distance_to(pos) ** 2
        np.testing.assert_allclose(a.squared_distance_to(pos), d)


def test_move():
    a = Entity(EntityType.GHOST)
    a.alive = True
    a.face(Direction.LEFT)

    # Move for 0 ticks
    old_pos = a.pos.copy()
    a.move(0)
    np.testing.assert_allclose(a.pos, old_pos)
    # Move when moving is False
    old_pos = a.pos.copy()
    a.moving = False
    a.move(1e3)
    np.testing.assert_allclose(a.pos, old_pos)
    a.moving = True
    # Move for n ticks
    ticks = 327.48
    old_pos = a.pos.copy() + a.direction.vector * a.speed * ticks
    a.move(ticks)
    np.testing.assert_allclose(a.pos, old_pos)


def test_teleport():
    a = Entity(EntityType.GHOST)

    for i in range(10):
        pos = np.random.random_sample(2) * 1000
        a.teleport(pos)
        assert (pos == a.pos).all()


def test_kill():
    a = Entity(EntityType.GHOST)
    a.alive = True

    a.kill()
    assert not a.alive


def test_default_collison_behavior():
    ghost = Entity(EntityType.GHOST)
    pacman = Entity(EntityType.PACMAN)

    assert not ghost.can_collide_with(ghost.type)
    assert ghost.can_collide_with(pacman.type)

    assert pacman.can_collide_with(ghost.type)
    assert pacman.can_collide_with(pacman.type)
