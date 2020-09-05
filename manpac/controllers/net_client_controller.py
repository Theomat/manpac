from manpac.utils.export_decorator import export
from manpac.controllers.abstract_controller import AbstractController
from manpac.controllers.net_message import parse, \
    MsgJoin, MsgResult, MsgSyncMap, MsgSyncEntity

import socket
import threading
import time


def _callback_result_(net_client_controller, msg, socket):
    net_client_controller.has_ok = msg.result


def _callback_sync_entity_(net_client_controller, msg, socket):
    entity = net_client_controller.game.entities[msg.uid]
    entity.teleport(msg.pos)
    entity.face(msg.direction)
    entity.alive = msg.alive

    if entity == net_client_controller.entity:
        net_client_controller._send_message_(MsgResult(True))


def _callback_sync_map_(net_client_controller, msg, socket):
    net_client_controller.game.map.terrain = msg.terrain
    net_client_controller._send_message_(MsgResult(True))
    net_client_controller.has_started = True


_CALLBACKS_ = {
    MsgResult.uid: _callback_result_,
    MsgSyncEntity.uid: _callback_sync_entity_,
    MsgSyncMap.uid: _callback_sync_map_
}


@export
class NetClientController(AbstractController):

    def __init__(self, controller, host="127.0.0.1", port=9999):
        super(NetClientController, self).__init__(controller.game)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.buffer_size = 4096
        self.has_started = False
        self.controller = controller

        self.host = host
        self.port = port

    def on_attach(self, entity):
        super(NetClientController, self).on_attach(entity)
        self.controller.on_attach(entity)

        server_thread = threading.Thread(target=self._listen_)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()

        self.socket.connect((self.host, self.port))
        print("Client: connected")
        self._notify_(MsgJoin(self.entity.type))

    def _listen_(self):
        while not self.socket._closed:
            msg = parse(self.socket.recv(self.buffer_size))
            print("Client: received=", msg)
            _CALLBACKS_[msg.uid](self, msg, self.socket)

    def on_game_start(self):
        while not self.has_started:
            time.sleep(.1)
        self.controller.on_game_start()

    def on_game_end(self):
        self.socket.close()
        self.controller.on_death()
        self.controller.on_game_end()

    def _notify_(self, msg):
        self.has_ok = False
        while not self.has_ok:
            self._send_message_(msg)
            time.sleep(.1)

    def on_death(self):
        self._send_message_(MsgSyncEntity(entity=self.entity))
        self.controller.on_death()

    def _send_message_(self, msg):
        if self.socket._closed:
            self.entity.alive = False
            return
        self.socket.sendall(msg.bytes())

    def _accept_(self, socket, client_address):
        self.client_address = client_address
        self.socket = socket
        self._send_message_(MsgResult(True))

    def update(self, ticks):
        self.controller.update(ticks)
        self._send_message_(MsgSyncEntity(entity=self.entity))
        for entity in self.game.entities:
            if entity != self.entity:
                self.game.map.move(entity, ticks)
