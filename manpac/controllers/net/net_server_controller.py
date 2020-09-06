from manpac.utils.export_decorator import export
from manpac.game_status import GameStatus
from manpac.controllers.abstract_controller import AbstractController
from manpac.modifiers.swap_modifier import SwapModifier
from manpac.controllers.net.net_message import parse, \
    MsgJoin, MsgResult, MsgSyncMap, MsgSyncEntity, MsgSyncClock, MsgCompound, \
    MsgSyncMapBoosts, MsgEndGame, MsgBoostPickup, MsgYourEntity, MsgStartGame, \
    MsgBoostUse, MsgSyncModifiers

import socketserver
import threading
from functools import partial
import time
import numpy as np


def _callback_join_(net_server_controller, msg, socket, client_address):
    if net_server_controller.free:
        if net_server_controller.entity.type == msg.type:
            net_server_controller._accept_(socket, client_address)
    else:
        socket.sendto(MsgResult(False).bytes(), client_address)


def _callback_result_(net_server_controller, msg, socket, client_address):
    net_server_controller.has_result = True
    net_server_controller.has_ok = msg.result


def _callback_sync_entity_(net_server_controller, msg, socket, client_address):
    net_server_controller.sync_message = msg


def _callback_boost_use_(net_server_controller, msg, socket, client_address):
    net_server_controller.entity.use_modifier()
    net_server_controller.sync_message = MsgSyncEntity(entity=net_server_controller.entity)
    net_server_controller._send_message_(net_server_controller.sync_message)


_CALLBACKS_ = {
    MsgJoin.uid: _callback_join_,
    MsgResult.uid: _callback_result_,
    MsgSyncEntity.uid: _callback_sync_entity_,
    MsgBoostUse.uid: _callback_boost_use_,
}


class NetServerHandler(socketserver.BaseRequestHandler):
    def __init__(self, net_server_controller, *args, **kwargs):
        self.net = net_server_controller
        super().__init__(*args, **kwargs)

    def handle(self):
        content, socket = self.request
        msg = parse(content)
        _CALLBACKS_[msg.uid](self.net, msg, socket, self.client_address)


@export
class NetServerController(AbstractController):
    """
    A controller that is a server and will take instructions from a remote client.

    Parameters
    -----------
    - *game*: (**Game**)
        the game this controller is being used in
    - *host*: (**string**)
        the host ip
    - *port*: (**int**)
        the port of the host
    """

    def __init__(self, game, host="127.0.0.1", port=9999):
        super(NetServerController, self).__init__(game)
        self.server = socketserver.UDPServer((host, port), partial(NetServerHandler, self), bind_and_activate=True)
        # Start listening
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        self.free = False
        self.client_address = None
        self.is_first_tick_done = False

        self.sync_message = None

        self.last_holdings = []
        self.last_modifiers = []

    def on_attach(self, entity):
        super(NetServerController, self).on_attach(entity)
        # Indicate that this controller is free for a remote client to take
        self.free = True

    def on_game_start(self):
        # Wait for a client to take this controller
        while self.client_address is None:
            time.sleep(.1)
        # Assign UID to each entity
        for i, entity in enumerate(self.game.entities):
            entity.uid = i
            self.last_holdings.append([])
            self.last_modifiers.append([])
        # Send map data
        self._notify_(MsgSyncMap(self.game.map.terrain))
        # Send your entity data
        self._send_message_(MsgYourEntity(self.entity.uid))
        # Send initial sync data
        for entity in self.game.entities:
            self._send_message_(MsgSyncEntity(entity=entity))

    def _notify_(self, msg):
        self.has_result = False
        self.has_ok = False
        while not self.has_result:
            self._send_message_(msg)
            time.sleep(.1)
        return self.has_ok

    def on_game_end(self):
        # Send that the game is done
        self._send_message_(MsgEndGame())
        self.server.shutdown()

    def on_death(self):
        # Be sure to send that this entity is now dead
        self._send_message_(MsgSyncEntity(entity=self.entity))

        # Keep the game updated
        # because update won't be called by the game anymore we have to do it
        def keep_updated():
            while self.game.status is GameStatus.ONGOING:
                self.update(1)
                time.sleep(.02)

        upd_thread = threading.Thread(target=keep_updated)
        upd_thread.daemon = True
        upd_thread.start()

    def on_boost_pickup(self):
        # On boost pickup send info
        self._send_message_(MsgBoostPickup(self.entity.uid, self.entity.holding))

    def _send_message_(self, msg):
        """
        Send the specified NetMessage.
        Parameters
        -----------
        - *msg*: (**NetMessage**)
            the message to be sent
        """
        self.socket.sendto(msg.bytes(), self.client_address)

    def _accept_(self, socket, client_address):
        self.client_address = client_address
        self.socket = socket
        self.free = False
        self._send_message_(MsgResult(True))

    def _should_send_pos_upd_(self, li):
        for boost in li:
            if isinstance(boost, SwapModifier):
                return True
        return False

    def update(self, ticks):
        # Tell the game has started
        if not self.is_first_tick_done:
            self.is_first_tick_done = True
            self._send_message_(MsgStartGame())
        # Make a compound message of the new positions
        messages = [MsgSyncEntity(entity=e) for e in self.game.entities
                    if self.entity != e]
        messages.append(MsgSyncClock(self.game.duration))
        self._send_message_(MsgCompound(*messages))
        # Sync map boosts
        self._send_message_(MsgSyncMapBoosts(self.game.map.ghost_boosts, self.game.map.pacman_boosts))
        # If has received an update info about entity update now
        if self.sync_message:
            entity = self.entity
            msg = self.sync_message
            dist = np.sum(np.abs(entity.pos - msg.pos))
            self.game.map._do_boost_pickup_(entity, dist)
            entity.face(msg.direction)
            entity.teleport(msg.pos)
            self.sync_message = None

        # Sync boost use / boost pickup
        for i, entity in enumerate(self.game.entities):
            if entity == self.entity:
                continue
            # Sync only on change
            if entity.holding != self.last_holdings[i]:
                if entity.holding:
                    self._send_message_(MsgBoostPickup(entity.uid, entity.holding))
                else:
                    self._send_message_(MsgBoostUse(entity.uid))
                self.last_holdings[i] = entity.holding
        # Sync modifiers
        for i, entity in enumerate(self.game.entities):
            # Sync only on change
            if entity.modifiers != self.last_modifiers[i]:
                self._send_message_(MsgSyncModifiers(entity.uid, entity.modifiers))
                # If a boost with a teleport was used, send local pos
                if self._should_send_pos_upd_(self.last_modifiers[i]):
                    self.sync_message = MsgSyncEntity(entity=self.entity)
                    self._send_message_(self.sync_message)
                self.last_modifiers[i] = entity.modifiers[:]
