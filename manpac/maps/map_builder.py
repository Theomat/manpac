from manpac.utils import export
from manpac.cell import Cell

import numpy as np
from types import SimpleNamespace


@export
def block(map, x, y, width, height):
    """
    Build a wall of the specified dimensions at the specified location.

    Parameters
    -----------
    - *map*: (**Map**)
        the map the block will be built on
    - *x*: (**int**)
        the x coordinate of the top left corner
    - *y*: (**int**)
        the y coordinate of the top left corner
    - *width*: (**int**)
        the width of the block
    - *height*: (**int**)
        the height of the block
    """
    map[x: x + width, y: y + height] = Cell.WALL


def _tee_down_(map, cx, cy, size):
    map[cx - size:cx + size + 1, cy] = Cell.WALL
    map[cx, cy: cy + size + 1] = Cell.WALL


def _tee_up_(map, cx, cy, size):
    map[cx - size:cx + size + 1, cy] = Cell.WALL
    map[cx, cy - size - 1: cy] = Cell.WALL


def _tee_left_(map, cx, cy, size):
    map[cx, cy - size:cy + size + 1] = Cell.WALL
    map[cx - size - 1:cx, cy] = Cell.WALL


def _tee_right_(map, cx, cy, size):
    map[cx, cy - size:cy + size + 1] = Cell.WALL
    map[cx: cx + size + 1, cy] = Cell.WALL


tee = SimpleNamespace(up=_tee_up_, down=_tee_down_, left=_tee_left_, right=_tee_right_)


@export
def make_horizontal_symmetric(map):
    """
    Make this map symmetric with respect to the centered X axis.
    Parameters
    -----------
    - *map*: (**Map**)
        the map to be made horizontally symetric
    """
    map.terrain += np.fliplr(map.terrain)
    np.clip(map.terrain, Cell.EMPTY, Cell.WALL, out=map.terrain)


@export
def make_vertical_symmetric(map):
    """
    Make this map symmetric with respect to the centered Y axis.
    Parameters
    -----------
    - *map*: (**Map**)
        the map to be made vertically symetric
    """
    map.terrain += np.flipud(map.terrain)
    np.clip(map.terrain, Cell.EMPTY, Cell.WALL, out=map.terrain)
