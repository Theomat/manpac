from manpac.utils import export

from enum import Enum
import numpy as np


@export
class Direction(Enum):
    """
    Represent a direction in which an entity can move.
    ```direction.vector``` is equal to the respective numpy vector representing the unit movement in that direction.
    """
    def __new__(cls, vector):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        obj.vector = vector
        return obj
    LEFT = np.array([-1, 0], dtype=np.int64)
    RIGHT = np.array([1, 0], dtype=np.int64)
    TOP = np.array([0, -1], dtype=np.int64)
    BOTTOM = np.array([0, 1], dtype=np.int64)

    def __neg__(self):
        if self == Direction.LEFT:
            return Direction.RIGHT
        elif self == Direction.RIGHT:
            return Direction.LEFT
        elif self == Direction.TOP:
            return Direction.BOTTOM
        elif self == Direction.BOTTOM:
            return Direction.TOP

    def __lt__(self, o):
        if isinstance(o, Direction):
            return self.value < o.value
        return self.value < o
