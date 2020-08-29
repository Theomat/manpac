from manpac.utils import export

from enum import Enum


@export
class GameStatus(Enum):
    """
    Represent a game status.
    """
    NOT_STARTED = "not started"
    ONGOING = "ongoing"
    FINISHED = "finished"
