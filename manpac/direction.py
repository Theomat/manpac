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
    UP = np.array([0, -1], dtype=np.int64)
    DOWN = np.array([0, 1], dtype=np.int64)

    def __neg__(self):
        if self == Direction.LEFT:
            return Direction.RIGHT
        elif self == Direction.RIGHT:
            return Direction.LEFT
        elif self == Direction.UP:
            return Direction.DOWN
        elif self == Direction.DOWN:
            return Direction.UP

    def __lt__(self, o):
        if isinstance(o, Direction):
            return self.value < o.value
        return self.value < o

    def rot90(self, n=1):
        """
        Return this direction rotated 90° clockwise n times.

        Parameters
        -----------
        - *n*: (**int**)
            the number of rotations that should be made
        Return
        -----------
        The corresponding direction.
        type: **Direction**
        """
        n = n & 3  # modulo 4
        if n == 0:
            return self
        next = self
        if self is Direction.LEFT:
            next = Direction.UP
        elif self is Direction.UP:
            next = Direction.RIGHT
        elif self is Direction.RIGHT:
            next = Direction.DOWN
        elif self is Direction.DOWN:
            next = Direction.LEFT
        return next.rot90(n-1)

    @classmethod
    def representing(cls, vector):
        """
        Return the list of directions that can be positive linear sum of the specified vector.

        Parameters
        -----------
        - *vector*: (**numpy.ndarray**)
            the vector to be used

        Return
        -----------
        A list of direction.
        type: **Direction list**
        """
        return [d for d in Direction if np.max(d.vector * vector) > 0]
