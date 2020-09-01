from manpac.entity_type import EntityType
from manpac.cell import Cell
from manpac.map import Map
from manpac.modifiers.speed_modifier import SpeedModifier
from manpac.boost_generators.simple_boost_generator import SimpleBoostGenerator

import numpy as np

def man_pacman(game):
    boost_generator = SimpleBoostGenerator(game,1,[(1,lambda:SpeedModifier(game,10,2))],[(1,lambda:SpeedModifier(game,10,2))])
    map = Map((21,28),boost_generator=boost_generator)

    for i in range(21):
        map[np.array([i,0])] = Cell.WALL
        map[np.array([i,27])] = Cell.WALL
    for i in range(9):
        map[np.array([0,i+1])] = Cell.WALL
        map[np.array([20,i+1])] = Cell.WALL
        map[np.array([4,i+9])] = Cell.WALL
        map[np.array([16,i+9])] = Cell.WALL
        map[np.array([0,i+18])] = Cell.WALL
        map[np.array([20,i+18])] = Cell.WALL
    for i in (0,4,10,14):
        map[np.array([2+i,2])] = Cell.WALL
        map[np.array([2+i,3])] = Cell.WALL
        map[np.array([2+i,4])] = Cell.WALL
        map[np.array([3+i,4])] = Cell.WALL
        map[np.array([3+i,2])] = Cell.WALL
        map[np.array([4+i,4])] = Cell.WALL
        map[np.array([4+i,3])] = Cell.WALL
        map[np.array([4+i,2])] = Cell.WALL
    for i in range(1,5):
        map[np.array([10,i])] = Cell.WALL
        map[np.array([i,9])] = Cell.WALL
        map[np.array([i+16,9])] = Cell.WALL
        map[np.array([i,18])] = Cell.WALL
        map[np.array([i+15,18])] = Cell.WALL
        map[np.array([6,14+i])] = Cell.WALL
        map[np.array([14,14+i])] = Cell.WALL
    for (i,j) in ((2,6),(16,6),(0,22),(18,22)):
        map[np.array([i,j])] = Cell.WALL
        map[np.array([i+1,j])] = Cell.WALL
        map[np.array([i+2,j])] = Cell.WALL
        map[np.array([i,j+1])] = Cell.WALL
        map[np.array([i+1,j+1])] = Cell.WALL
        map[np.array([i+2,j+1])] = Cell.WALL
    for j in (6,17,22):
        map[np.array([8,j])] = Cell.WALL
        map[np.array([9,j])] = Cell.WALL
        map[np.array([10,j])] = Cell.WALL
        map[np.array([11,j])] = Cell.WALL
        map[np.array([12,j])] = Cell.WALL
        map[np.array([8,j+1])] = Cell.WALL
        map[np.array([9,j+1])] = Cell.WALL
        map[np.array([10,j+1])] = Cell.WALL
        map[np.array([11,j+1])] = Cell.WALL
        map[np.array([12,j+1])] = Cell.WALL
    for i in range(3):
        map[np.array([6,6+i])] = Cell.WALL
        map[np.array([6+i,9])] = Cell.WALL
        map[np.array([6,10+i])] = Cell.WALL
        map[np.array([14,6+i])] = Cell.WALL
        map[np.array([12+i,9])] = Cell.WALL
        map[np.array([14,10+i])] = Cell.WALL
        map[np.array([6+i,20])] = Cell.WALL
        map[np.array([2+i,20])] = Cell.WALL
        map[np.array([16+i,20])] = Cell.WALL
        map[np.array([12+i,20])] = Cell.WALL
        map[np.array([4,21+i])] = Cell.WALL
        map[np.array([16,21+i])] = Cell.WALL
        map[np.array([10,23+i])] = Cell.WALL
        map[np.array([14,22+i])] = Cell.WALL
        map[np.array([6,22+i])] = Cell.WALL
        map[np.array([10,18+i])] = Cell.WALL
        map[np.array([10,7+i])] = Cell.WALL
    for i in range(7):
        map[np.array([2+i,25])] = Cell.WALL
        map[np.array([12+i,25])] = Cell.WALL
    for i in range(5):
        map[np.array([8+i,15])] = Cell.WALL
        map[np.array([8,11+i])] = Cell.WALL
        map[np.array([12,11+i])] = Cell.WALL
    map[np.array([9,11])] = Cell.WALL
    map[np.array([11,11])] = Cell.WALL
    map[np.array([6,14])] = Cell.WALL
    map[np.array([14,14])] = Cell.WALL
    map.spawns[EntityType.GHOST] = np.array([10.5,10.5])
    map.spawns[EntityType.PACMAN] = np.array([10, 14])

    return map
