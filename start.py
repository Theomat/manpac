from manpac.ui.interface import Interface
from manpac.game import Game
from manpac.entity_type import EntityType
from manpac.entity import Entity
from manpac.controllers.target_seeker_controller import TargetSeekerController
from manpac.controllers.random_walk_controller import RandomWalkController
from manpac.controllers.human_controller import HumanController
from manpac.controllers.walk_away_controller import WalkAwayController
from manpac.maps.map_pacman import MapPacman


ghosts = []
for i in range(4):
    ghosts.append(Entity(EntityType.GHOST))

pacman = Entity(EntityType.PACMAN)

game = Game(pacman, *ghosts)
hasHuman = False
hasRandom = False
for ghost in ghosts:
    if not hasHuman:
        ghost.attach(HumanController(game))
        hasHuman = True
    elif not hasRandom:
        hasRandom = True
        ghost.attach(RandomWalkController(game, 60*2))
    else:
        ghost.attach(WalkAwayController(game, 60*2))

# pacman.attach(RandomWalkController(game, 60))
pacman.attach(TargetSeekerController(game))

map = MapPacman(game)

interface = Interface(game)
interface.start(map)
