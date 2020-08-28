from manpac.direction import Direction

import numpy as np


def test_quantity():
    assert len(Direction) == 4


def test_equal():
    for direction in Direction:
        assert direction == direction
        assert not (-direction == direction)


def test_negation():
    for direction in Direction:
        assert not (-direction.vector + direction.vector).all()


def test_length():
    for direction in Direction:
        assert np.linalg.norm(direction.vector) == 1
