from manpac.utils.export_decorator import export
from manpac.game_status import GameStatus
from manpac.controllers.abstract_controller import AbstractController
from manpac.controllers.net.net_message import parse, \
    MsgJoin, MsgResult, MsgSyncMap, MsgSyncEntity, MsgSyncClock, MsgSyncMapBoosts, \
    MsgEndGame, MsgBoostPickup

import socket
import threading
import time


def _callback_result_(net_client_controller, msg, socket):
    net_client_controller.has_ok = msg.result


def _callback_sync_entity_(net_client_controller, msg, socket):
    entity = net_client_controller.game.entities[msg.ent_uid]
    entity.teleport(msg.pos)
    entity.face(msg.direction)
    entity.alive = msg.alive
    entity.uid = msg.ent_uid

    if entity == net_client_controller.entity:
        net_client_controller._send_message_(MsgResult(True))


def _callback_sync_map_(net_client_controller, msg, socket):
    net_client_controller.terrain = msg.terrain
    net_client_controller._send_message_(MsgResult(True))
    net_client_controller.has_started = True


def _callback_sync_clock_(net_client_controller, msg, socket):
    net_client_controller.net_ticks = msg.ticks - net_client_controller.game.duration


def _callback_sync_map_boosts_(net_client_controller, msg, socket):
    if net_client_controller.game.map:
        net_client_controller.game.map.ghost_boosts = msg.ghost_boosts
        net_client_controller.game.map.pacman_boosts = msg.pacman_boosts


def _callback_end_game_(net_client_controller, msg, socket):
    net_client_controller.game.status = GameStatus.FINISHED


def _callback_boost_pickup_(net_client_controller, msg, socket):
    msg.parse_boost(net_client_controller.game)
    entity = net_client_controller.game.entities[msg.ent_uid]
    entity.pickup(msg.boost)


_CALLBACKS_ = {
    MsgResult.uid: _callback_result_,
    MsgSyncEntity.uid: _callback_sync_entity_,
    MsgSyncMap.uid: _callback_sync_map_,
    MsgSyncClock.uid: _callback_sync_clock_,
    MsgSyncMapBoosts.uid: _callback_sync_map_boosts_,
    MsgEndGame.uid: _callback_end_game_,
    MsgBoostPickup.uid: _callback_boost_pickup_,
}


@export
class NetClientController(AbstractController):

    def __init__(self, controller, host="127.0.0.1", port=9999):
        super(NetClientController, self).__init__(controller.game)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.buffer_size = 4096
        self.has_started = False
        self.controller = controller

        self.net_ticks = 0
        self.taken = 0

        self.max_ticks_in_advance = 30

        self.host = host
        self.port = port

    def on_attach(self, entity):
        super(NetClientController, self).on_attach(entity)
        self.controller.on_attach(entity)

        ret_code = self.socket.connect_ex((self.host, self.port))
        if not ret_code == 0:
            print("Failed to connect to: host=", self.host, "port=", self.port)
            print("Error code=", ret_code)
            exit()

        server_thread = threading.Thread(target=self._listen_)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()

        self._notify_(MsgJoin(self.entity.type))

    def _listen_(self):
        while not self.socket._closed:
            data = self.socket.recv(self.buffer_size)
            msg = parse(data)
            if msg.compound:
                for msg in msg.messages:
                    _CALLBACKS_[msg.uid](self, msg, self.socket)
            else:
                _CALLBACKS_[msg.uid](self, msg, self.socket)

    def on_game_start(self):
        self.entity.uid = -5
        while not self.has_started and not self.entity.uid >= 0:
            time.sleep(.1)
        self.controller.on_game_start()
        self.game.map.terrain = self.terrain
        self.game.map.boost_generator = None
        self.game.map.compiled = False
        self.game.map.compile()

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

    def on_boost_pickup(self):
        self.controller.on_boost_pickup()

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
        if -self.net_ticks >= self.max_ticks_in_advance:
            return
        if self.net_ticks >= self.max_ticks_in_advance:
            ticks *= 2

        if self.entity.alive:
            self.controller.update(ticks)
        self._send_message_(MsgSyncEntity(entity=self.entity))
        if self.net_ticks <= 0:
            for entity in self.game.entities:
                if entity != self.entity:
                    self.game.map.move(entity, ticks)
