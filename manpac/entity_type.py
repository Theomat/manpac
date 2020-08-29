from manpac.utils import export

from enum import Enum


@export
class EntityType(Enum):
    """
    Represent an entity type.
    """
    PACMAN = "pacman"
    GHOST = "ghost"
