from manpac.utils import export

from enum import IntEnum


@export
class Cell(IntEnum):
    """
    Represent a cell.
    """
    EMPTY = 0
    WALL = 1

    @property
    def walkable(self):
        return self is Cell.EMPTY
