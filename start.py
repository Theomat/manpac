from manpac.ui.interface import Interface
from manpac.game import Game
from manpac.entity_type import EntityType
from manpac.entity import Entity
from manpac.controllers.random_walk_controller import RandomWalkController
from manpac.controllers.target_seeker_controller import TargetSeekerController
from manpac.map import Map

import numpy as np


ghosts = []
for i in range(4):
    a = Entity(EntityType.GHOST)
    ghosts.append(a)

pacman = Entity(EntityType.PACMAN)

game = Game(pacman, *ghosts)
for ghost in ghosts:
    a.attach(RandomWalkController(game, 20))
pacman.attach(TargetSeekerController(game))


map = Map((40, 40))
map.spawns[EntityType.GHOST] = np.array([37, 37])


interface = Interface(game)
interface.start(map)
