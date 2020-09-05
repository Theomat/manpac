#!/usr/bin/env python
from os import environ
# Hide pygame hello message
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

from manpac.maps.map_pacman import MapPacman
from manpac.entity import Entity
from manpac.entity_type import EntityType
from manpac.game import Game
from manpac.game_status import GameStatus
from manpac.controllers.human_controller import HumanController
from manpac.controllers.random_walk_controller import RandomWalkController
from manpac.controllers.walk_away_controller import WalkAwayController
from manpac.controllers.target_seeker_controller import TargetSeekerController
from manpac.controllers.net_server_controller import NetServerController
from manpac.controllers.net_client_controller import NetClientController

from manpac.ui.interface import Interface

import argparse
from tqdm import trange


MAP_DICT = {
    "pacman": lambda game: MapPacman(game)
}
CONTROLLER_DICT = {
    "n": lambda game: None,
    "t": lambda game: TargetSeekerController(game),
    "hu": lambda game: HumanController(game),
    "rw": lambda game: RandomWalkController(game),
    "wa": lambda game: WalkAwayController(game, 10),
    "ns": lambda game: NetServerController(game),
    "nc": lambda game: NetClientController(HumanController(game)),
    "ncrw": lambda game: NetClientController(RandomWalkController(game))
}
# =============================================================================
#  ARGUMENT PARSING
# =============================================================================
parser = argparse.ArgumentParser(description='Run manpac games.')

game_options = parser.add_argument_group('game options')
default_map = list(MAP_DICT.keys())[0]
game_options.add_argument('-c', '--controllers', dest='controllers_name',
                          action='store', type=str,
                          choices=list(CONTROLLER_DICT.keys()),
                          nargs=4, required=True,
                          help='the controllers pacman and ghosts will use (required)')
game_options.add_argument('-m', '--map', dest='map_name',
                          action='store', default=default_map, type=str,
                          choices=list(MAP_DICT.keys()),
                          help='the map (default: "{}")'.format(default_map))
game_options.add_argument('--pacman', dest='pacman_controller',
                          action='store', type=str, default="t",
                          choices=list(CONTROLLER_DICT.keys()),
                          help='the controller for pacman (default: "t")')
game_options.add_argument('--no-pac', dest='no_pacman',
                          action='store_true',
                          help='no pacman')
game_options.add_argument('-n', dest='games',
                          action='store', default=1, type=int,
                          help='the number of games (default: 1)')

misc_options = parser.add_argument_group('misc options')
misc_options.add_argument('-p', '--progress', dest='progress',
                          action='store_true', default=False,
                          help='display a progress bar in the console')
misc_options.add_argument('--ui', dest='ui',
                          action='store_true', default=False,
                          help='show user interface')
misc_options.add_argument('-d', '--debug', dest='debug',
                          action='store_true', default=False,
                          help='activate debug mode')

params = parser.parse_args()
# =============================================================================
# RUNNING GAMES
# =============================================================================
game_range = trange(params.games) if params.progress else range(params.games)
for game_num in game_range:
    # Create pacmans
    pacmans = []
    if not params.no_pacman:
        pacmans.append(Entity(EntityType.PACMAN))
    # Create ghosts
    ghosts = []
    for i in range(4):
        ghosts.append(Entity(EntityType.GHOST))
    # Create game
    game = Game(*pacmans, *ghosts)

    # Attach controller off pacman
    for pacman in pacmans:
        controller = CONTROLLER_DICT[params.pacman_controller](game)
        if controller is None:
            continue
        controller.debug = params.debug
        pacman.attach(controller)

    # Attach controller off ghosts
    for ghost, controller in zip(ghosts, params.controllers_name):
        controller = CONTROLLER_DICT[controller](game)
        if controller is None:
            continue
        controller.debug = params.debug
        ghost.attach(controller)

    # Create map
    map = MAP_DICT[params.map_name](game)
    # Run the game
    if params.ui:
        interface = Interface(game)
        interface.start(map)
    else:
        game.start(map)
        while game.status is not GameStatus.FINISHED:
            game.update(100)

    print(game.duration)
