from manpac.entity_type import EntityType
from manpac.entity import Entity
from manpac.map import Map
from manpac.direction import Direction
from manpac.cell import Cell


import numpy as np
import pytest


def test_get_set():
    map = Map((10, 10))
    # Assert start empty
    cnt = 0
    for row in map[:, :]:
        for x in row:
            if x == Cell.EMPTY:
                cnt += 1
    assert cnt == 100

    # Test basic indexing
    map[0, 0] = Cell.WALL
    assert map[0, 0] == Cell.WALL

    # Test with numpy arrays
    pos = np.array([4, 5])
    map[pos] = Cell.WALL
    assert map[pos] == Cell.WALL

    cnt = 0
    for row in map[:, :]:
        for x in row:
            if x == Cell.WALL:
                cnt += 1
    assert cnt == 2


def test_move():
    map = Map((10, 10))
    ent = Entity(EntityType.GHOST)
    ent.alive = True
    ent.moving = True
    ent.face(Direction.RIGHT)

    # Move 0 ticks
    old_pos = ent.pos.copy()
    map.move(ent, 0)
    np.testing.assert_allclose(ent.pos, old_pos)
    # Move for n ticks
    ticks = 7.5
    old_pos = ent.pos.copy() + ent.direction.vector * ent.speed * ticks
    map.move(ent, ticks)
    np.testing.assert_allclose(ent.pos, old_pos)


def test_closest_walkable():
    map = Map((10, 10))

    assert (map.closest_walkable(np.array([-1, 0])) == np.array([0, 0])).all()
    assert (map.closest_walkable(np.array([0, -1])) == np.array([0, 0])).all()
    assert (map.closest_walkable(np.array([10, 9])) == np.array([9, 9])).all()
    assert (map.closest_walkable(np.array([9, 10])) == np.array([9, 9])).all()

    pos = [4, 5]

    for i in range(10):
        n = np.random.random(1)[0]
        assert (map.closest_walkable(np.array([-n, 0])) == np.array([0, 0])).all()
        assert (map.closest_walkable(np.array([0, -n])) == np.array([0, 0])).all()
        assert (map.closest_walkable(np.array([9 + n, 9])) == np.array([9, 9])).all()
        assert (map.closest_walkable(np.array([9, 9 + n])) == np.array([9, 9])).all()
        n = n / 2
        assert (map.closest_walkable(np.array([4-n, 5])) == pos).all()
        assert (map.closest_walkable(np.array([4, 5-n])) == pos).all()
        assert (map.closest_walkable(np.array([4 + n, 5])) == pos).all()
        assert (map.closest_walkable(np.array([4, 5 + n])) == pos).all()

    map[pos] = Cell.WALL
    for i in range(10):
        n = np.random.random(1)[0]
        n = n / 2
        assert not (map.closest_walkable(np.array([4-n, 5])) == pos).all()
        assert not (map.closest_walkable(np.array([4, 5-n])) == pos).all()
        assert not (map.closest_walkable(np.array([4 + n, 5])) == pos).all()
        assert not (map.closest_walkable(np.array([4, 5 + n])) == pos).all()


@pytest.mark.timeout(5)
def test_move_bounds():
    size = 10
    map = Map((size, size))
    ent = Entity(EntityType.GHOST)
    ent.alive = True
    ent.moving = True
    ticks = 7785888.5

    for direction in Direction:
        for i in range(10):
            ent.face(direction)
            p = np.clip(np.random.random_sample(2) * size, ent.size, size - ent.size)
            ent.teleport(p)

            # Move for n ticks
            old_pos = ent.pos.copy() + ent.direction.vector * ent.speed * ticks
            old_pos = np.clip(old_pos, ent.size, size - ent.size)
            map.move(ent, ticks)
            np.testing.assert_allclose(ent.pos, old_pos)

            #  Move for n ticks
            ent.face(-ent.direction)
            old_pos = ent.pos.copy() + ent.direction.vector * ent.speed * ticks
            old_pos = np.clip(old_pos, ent.size, size - ent.size)
            map.move(ent, ticks)
            np.testing.assert_allclose(ent.pos, old_pos)


@pytest.mark.timeout(5)
def test_move_walls():
    size = 10
    map = Map((size, size))
    ent = Entity(EntityType.GHOST)
    ent.alive = True
    ent.moving = True
    ticks = 7785888.5

    map[:, 7:] = Cell.WALL
    map[8:, :] = Cell.WALL
    map[:1, :] = Cell.WALL
    map[:, :2] = Cell.WALL
    max_bounds = np.array([8, 7]) - ent.size
    min_bounds = np.array([1, 2]) + ent.size

    for direction in Direction:
        for i in range(10):
            ent.face(direction)
            p = np.clip(np.random.random_sample(2) * (size - 1), min_bounds, max_bounds)
            ent.teleport(p)

            map.print()

            # Move for n ticks
            old_pos = ent.pos.copy() + ent.direction.vector * ent.speed * ticks
            old_pos = np.clip(old_pos, min_bounds, max_bounds)
            map.move(ent, ticks)
            np.testing.assert_allclose(ent.pos, old_pos)

            #  Move for n ticks
            ent.face(-ent.direction)
            old_pos = ent.pos.copy() + ent.direction.vector * ent.speed * ticks
            old_pos = np.clip(old_pos, min_bounds, max_bounds)
            map.move(ent, ticks)
            np.testing.assert_allclose(ent.pos, old_pos)


def test_pickup_boost():
    map = Map((10, 10))
    ghost = Entity(EntityType.GHOST)
    ghost.alive = True
    ghost.moving = True
    ghost.face(Direction.RIGHT)

    pacman = Entity(EntityType.PACMAN)
    pacman.alive = True
    pacman.moving = True
    pacman.face(Direction.RIGHT)

    map.ghost_boosts = [[Direction.RIGHT.vector * 2.5, 9999], [Direction.DOWN.vector * 3.5, 9999]]

    # Pick up nothing
    map.move(pacman, 1)
    map.move(ghost, 1)
    assert len(map.ghost_boosts) == 2
    assert len(map.pacman_boosts) == 0

    # Pick up ghost boost
    ticks = 4 / ghost.speed
    map.move(pacman, ticks)
    map.move(ghost, ticks)
    assert len(map.ghost_boosts) == 1
    assert len(map.pacman_boosts) == 1

    # Pick up pacman boost
    ghost.face(-ghost.direction)
    pacman.face(-pacman.direction)
    map.move(ghost, ticks)
    map.move(pacman, ticks)
    assert len(map.ghost_boosts) == 1
    assert len(map.pacman_boosts) == 0
