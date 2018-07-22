import socket

import manager
from log import log


class ReceptionManager(manager.Manager):
    __slots__ = ['clnthndlr', 'managers']

    def __init__(self, clnthndlr, managers):
        self.clnthndlr = clnthndlr
        self.managers = managers

    def _handle_reception(self):
        self.clnthndlr.conn.setblocking(0)

        data = self.clnthndlr.handle_receiving_data()

        packet_id = data.packet_id

        for man in self.managers:
            if man.responds_to(packet_id):
                man.handle_request(self.clnthndlr, packet_id, data)
                break

    def init(self):
        pass

    def loop(self):
        try:
            self._handle_reception()
        except socket.error as e:
            if str(e) == "[WinError 10035] A non-blocking socket operation could not be completed immediately":
                return

            if not str(e) == "[WinError 10054] An existing connection was forcibly closed by the remote host":
                log(e)
            self.clnthndlr.isConnected = False
        #self.clnthndlr.conn.setblocking(1)