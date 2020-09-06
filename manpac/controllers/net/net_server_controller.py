from manpac.utils.export_decorator import export
from manpac.controllers.abstract_controller import AbstractController
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
    net_server_controller.has_ok = msg.result


def _callback_sync_entity_(net_server_controller, msg, socket, client_address):
    entity = net_server_controller.entity
    if net_server_controller.game.map._do_boost_pickup_(entity, np.sum(np.abs(entity.pos - msg.pos))):
        pass
    entity.face(msg.direction)
    entity.teleport(msg.pos)
    entity.alive = msg.alive


def _callback_boost_use_(net_server_controller, msg, socket, client_address):
    net_server_controller.entity.use_modifier()
    net_server_controller._send_message_(MsgSyncEntity(entity=net_server_controller.entity))


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

    def __init__(self, game, host="127.0.0.1", port=9999):
        super(NetServerController, self).__init__(game)
        self.server = socketserver.UDPServer((host, port), partial(NetServerHandler, self), bind_and_activate=True)
        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=self.server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()

        self.free = False
        self.client_address = None
        self.first_tick = True

        self.last_holdings = []
        self.last_modifiers = []

    def on_attach(self, entity):
        super(NetServerController, self).on_attach(entity)
        self.free = True

    def on_game_start(self):
        while self.client_address is None:
            time.sleep(.1)
        # UID for each
        for i, entity in enumerate(self.game.entities):
            entity.uid = i
            self.last_holdings.append([])
            self.last_modifiers.append([])
        self._notify_(MsgSyncMap(self.game.map.terrain))
        self._send_message_(MsgYourEntity(self.entity.uid))
        for entity in self.game.entities:
            self._send_message_(MsgSyncEntity(entity=entity))

    def _notify_(self, msg):
        self.has_ok = False
        while not self.has_ok:
            self._send_message_(msg)
            time.sleep(.1)

    def on_game_end(self):
        self._send_message_(MsgEndGame())
        self.server.shutdown()

    def on_death(self):
        self._send_message_(MsgSyncEntity(entity=self.entity))

    def on_boost_pickup(self):
        self._send_message_(MsgBoostPickup(self.entity.uid, self.entity.holding))

    def _send_message_(self, msg):
        self.socket.sendto(msg.bytes(), self.client_address)

    def _accept_(self, socket, client_address):
        self.client_address = client_address
        self.socket = socket
        self.free = False
        self._send_message_(MsgResult(True))

    def update(self, ticks):
        if self.first_tick:
            self.first_tick = False
            self._send_message_(MsgStartGame())
        messages = [MsgSyncEntity(entity=e) for e in self.game.entities
                    if self.entity != e]
        messages.append(MsgSyncClock(self.game.duration))
        self._send_message_(MsgCompound(*messages))
        self._send_message_(MsgSyncMapBoosts(self.game.map.ghost_boosts, self.game.map.pacman_boosts))
        for i, entity in enumerate(self.game.entities):
            if entity == self.entity:
                continue
            if entity.holding != self.last_holdings[i]:
                if entity.holding:
                    self._send_message_(MsgBoostPickup(entity.uid, entity.holding))
                else:
                    self._send_message_(MsgBoostUse(entity.uid))
                self.last_holdings[i] = entity.holding
        for i, entity in enumerate(self.game.entities):
            if entity == self.entity:
                continue
            if entity.modifiers != self.last_modifiers[i]:
                self._send_message_(MsgSyncModifiers(entity.uid, entity.modifiers))
                self.last_modifiers[i] = entity.modifiers[:]
