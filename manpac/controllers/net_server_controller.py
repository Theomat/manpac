from manpac.utils.export_decorator import export
from manpac.controllers.abstract_controller import AbstractController
from manpac.controllers.net_message import parse, \
    MsgJoin, MsgResult, MsgSyncMap, MsgSyncEntity

import socketserver
import threading
from functools import partial
import time


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
    entity.teleport(msg.pos)
    entity.face(msg.direction)
    entity.alive = msg.alive


_CALLBACKS_ = {
    MsgJoin.uid: _callback_join_,
    MsgResult.uid: _callback_result_,
    MsgSyncEntity.uid: _callback_sync_entity_,
}


class NetServerHandler(socketserver.BaseRequestHandler):
    def __init__(self, net_server_controller, *args, **kwargs):
        self.net = net_server_controller
        super().__init__(*args, **kwargs)

    def handle(self):
        content, socket = self.request
        msg = parse(content)
        print("Server: received ", msg)
        _CALLBACKS_[msg.uid](self.net, msg, socket, self.client_address)


@export
class NetServerController(AbstractController):

    def __init__(self, game, ip="127.0.0.1", port=9999):
        super(NetServerController, self).__init__(game)
        print("Listening on:", ip, "on port", port)
        self.server = socketserver.UDPServer((ip, port), partial(NetServerHandler, self), bind_and_activate=True)
        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=self.server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()

        self.free = False
        self.client_address = None

    def on_attach(self, entity):
        super(NetServerController, self).on_attach(entity)
        self.free = True

    def on_game_start(self):
        while self.client_address is None:
            time.sleep(.1)
        # UID for each
        for i, entity in enumerate(self.game.entities):
            entity.uid = i
        self._notify_(MsgSyncMap(self.game.map.terrain))
        for entity in self.game.entities:
            self._send_message_(MsgSyncEntity(entity=entity))

    def _notify_(self, msg):
        self.has_ok = False
        while not self.has_ok:
            self._send_message_(msg)
            time.sleep(.1)

    def on_game_end(self):
        self.server.shutdown()

    def on_death(self):
        self._send_message_(MsgSyncEntity(entity=self.entity))

    def _send_message_(self, msg):
        print("Server: sent", msg)
        self.socket.sendto(msg.bytes(), self.client_address)

    def _accept_(self, socket, client_address):
        self.client_address = client_address
        self.socket = socket
        self.free = False
        self._send_message_(MsgResult(True))

    def update(self, ticks):
        for entity in self.game.entities:
            if entity != self.entity:
                self._send_message_(MsgSyncEntity(entity=entity))
