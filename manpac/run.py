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
from manpac.controllers.net.net_server_controller import NetServerController
from manpac.controllers.net.net_client_controller import NetClientController
from manpac.ui.interface import Interface

import argparse
from tqdm import trange
import time


MAP_DICT = {
    "pacman": lambda game: MapPacman(game)
}
CONTROLLER_DICT = {
    "n": lambda game, params: None,
    "t": lambda game, params: TargetSeekerController(game),
    "hu": lambda game, params: HumanController(game),
    "rw": lambda game, params: RandomWalkController(game),
    "wa": lambda game, params: WalkAwayController(game, 10),
    "ns": lambda game, params: NetServerController(game, params.host, params.port),
    "nc": lambda game, params: NetClientController(HumanController(game), params.host, params.port)
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
                          nargs='*', default=[],
                          help='the controllers pacman and ghosts will use')
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
misc_options.add_argument('--progress', dest='progress',
                          action='store_true', default=False,
                          help='display a progress bar in the console')
misc_options.add_argument('--ui', dest='ui',
                          action='store_true', default=False,
                          help='show user interface')
misc_options.add_argument('-d', '--debug', dest='debug',
                          action='store_true', default=False,
                          help='activate debug mode')
misc_options.add_argument('-f', '--freq', dest='freq',
                          action='store', default=0, type=int,
                          help='frequence of the game update when no ui (default: unlimited)')

net_options = parser.add_argument_group('net options')
net_options.add_argument('--host', dest='host',
                         action='store', default="127.0.0.1",
                         help='host for net services (default: "127.0.0.1")')
net_options.add_argument('-p', '--port', dest='port',
                         action='store', default=9999, type=int,
                         help='port for net services (default: 9999)')

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

    params.controllers_name += ["n"] * (4 - len(params.controllers_name))
    # Create ghosts
    ghosts = []
    for i in range(4):
        ghosts.append(Entity(EntityType.GHOST))
    # Create game
    game = Game(*pacmans, *ghosts)

    # Attach controller off pacman
    for pacman in pacmans:
        controller = CONTROLLER_DICT[params.pacman_controller](game, params)
        if controller is None:
            continue
        controller.debug = params.debug
        pacman.attach(controller)

    # Attach controller off ghosts
    for ghost, controller in zip(ghosts, params.controllers_name):
        controller = CONTROLLER_DICT[controller](game, params)
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

        has_server = False
        for entity in game.entities:
            if isinstance(entity.controller, NetServerController):
                has_server = True
                break

        if has_server:
            time.sleep(3)

        while game.status is GameStatus.NOT_STARTED:
            time.sleep(.01)
        sleep_time = 1 / params.freq if params.freq > 0 else 0
        while game.status is not GameStatus.FINISHED:
            game.update(1)
            if sleep_time > 0:
                time.sleep(sleep_time)
