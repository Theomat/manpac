from manpac.ui.interface import Interface
from manpac.game import Game
from manpac.entity_type import EntityType
from manpac.entity import Entity
from manpac.cell import Cell
from manpac.controllers.random_walk_controller import RandomWalkController
from manpac.controllers.target_seeker_controller import TargetSeekerController
from manpac.controllers.human_controller import HumanController
from manpac.map import Map
from manpac.maps.map_pacman import *

import numpy as np


ghosts = []
for i in range(4):
    ghosts.append(Entity(EntityType.GHOST))

pacman = Entity(EntityType.PACMAN)

game = Game(pacman, *ghosts)
n = True
for ghost in ghosts:
    if n:
        ghost.attach(HumanController(game))
        n = False
    else:
        ghost.attach(RandomWalkController(game, 60 * 2))
pacman.attach(TargetSeekerController(game))

#map = Map((40, 40))
#for i in range(30):
#    map[np.random.randint(0, 40 - 1, 2)] = Cell.WALL
#map.spawns[EntityType.GHOST] = np.array([20, 20])
#map.spawns[EntityType.PACMAN] = np.array([1, 1])

map = man_pacman()

interface = Interface(game)
interface.start(map)
