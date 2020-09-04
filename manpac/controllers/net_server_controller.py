from manpac.utils.export_decorator import export
from manpac.controllers.abstract_controller import AbstractController


import socketserver


@export
class NetServerController(AbstractController, socketserver.DatagramRequestHandler):

    def __init__(self, game, ip, port):
        super(NetServerController, self).__init__(game)
        print("Listening on:", ip, "on port", port)
        self.server = socketserver.ThreadingUDPServer((ip, port), self, bind_and_activate=True)

    def setup(self):
        pass

    def handle(self):
        print("request:", self.request)
        print("client address:", self.client_address)

    def on_death(self):
        self.server.shutdown()
