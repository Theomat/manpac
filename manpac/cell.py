from manpac.utils import export

from enum import IntEnum


@export
class Cell(IntEnum):
    """
    Represent a cell.
    """
    EMPTY = 0
    WALL = 1
    DEBUG = 2
    DEBUG_ONCE = 3

    @property
    def walkable(self):
        return self is not Cell.WALL
