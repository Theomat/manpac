from manpac.utils import export
from manpac.entity_type import EntityType
from manpac.cell import Cell
from manpac.map import Map
from manpac.modifiers.speed_modifier import SpeedModifier
from manpac.modifiers.swap_modifier import SwapModifier
from manpac.modifiers.ghost_block_modifier import GhostBlockModifier
from manpac.modifiers.intangible_modifier import IntangibleModifier
from manpac.boost_generators.simple_boost_generator import SimpleBoostGenerator
import manpac.maps.map_builder as build


import numpy as np


@export
class MapPacman(Map):

    def __init__(self, game):
        ghost_factory = [(1, lambda:SpeedModifier(game, 2 * 60, 2)),
                         (1, lambda:SwapModifier(game, 10)),
                         (1, lambda:GhostBlockModifier(game, 2 * 60)),
                         (1, lambda:IntangibleModifier(game, 2 * 60))]
        pacman_factory = [(1, lambda:SpeedModifier(game, 2 * 60, 2))]
        boost_generator = SimpleBoostGenerator(game, .0, ghost_factory, pacman_factory)
        super(MapPacman, self).__init__((21, 28), boost_generator)

        # Borders of the map
        build.block(self, 0, 0, 21, 1)
        build.block(self, 0, 27, 21, 1)

        build.block(self, 0, 1, 1, 9)
        build.block(self, 20, 1, 1, 9)
        build.block(self, 4, 9, 1, 9)
        build.block(self, 16, 9, 1, 9)
        build.block(self, 0, 18, 1, 9)
        build.block(self, 20, 18, 1, 9)

        # Border part that links top and bottom part of the map
        build.block(self, 16, 9, 5, 10)
        build.block(self, 0, 9, 5, 10)

        # Thing the comes inwards at the center at the top
        build.block(self, 10, 1, 1, 4)

        # Top Blocks 3x3
        for i in (0, 4, 10, 14):
            build.block(self, 2+i, 2, 3, 3)

        # Vertical line around the center
        build.block(self, 6, 14, 1, 5)
        build.block(self, 14, 14, 1, 5)

        # Small top blocks
        build.block(self, 2, 6, 3, 2)
        build.block(self, 16, 6, 3, 2)

        # Blocks that come back inside at the bottom of the map on the sides
        build.block(self, 1, 22, 2, 2)
        build.block(self, 18, 22, 2, 2)

        # Horizontal part of the T
        for j in (6, 17, 22):
            build.block(self, 8, j, 5, 2)

        for i in range(3):
            self[6, 6+i] = Cell.WALL
            self[6+i, 9] = Cell.WALL
            self[6, 10+i] = Cell.WALL
            self[14, 6+i] = Cell.WALL
            self[12+i, 9] = Cell.WALL
            self[14, 10+i] = Cell.WALL
            self[6+i, 20] = Cell.WALL
            self[2+i, 20] = Cell.WALL
            self[16+i, 20] = Cell.WALL
            self[12+i, 20] = Cell.WALL
            self[4, 21+i] = Cell.WALL
            self[16, 21+i] = Cell.WALL
            self[10, 23+i] = Cell.WALL
            self[14, 22+i] = Cell.WALL
            self[6, 22+i] = Cell.WALL
            self[10, 18+i] = Cell.WALL
            self[10, 7+i] = Cell.WALL

        # Bottom horizontal lines
        build.block(self, 2, 25, 7, 1)
        build.block(self, 12, 25, 7, 1)

        # Central block
        build.block(self, 8, 15, 5, 1)
        build.block(self, 8, 11, 1, 5)
        build.block(self, 12, 11, 1, 5)

        # Last walls to finish cell
        self[9, 11] = Cell.WALL
        self[11, 11] = Cell.WALL

        self.spawns[EntityType.GHOST] = np.array([10, 10], dtype=np.int)
        self.spawns[EntityType.PACMAN] = np.array([10, 26], dtype=np.int)
