import socket

import manager
from log import log


class ReceptionManager(manager.Manager):

    def __init__(self, clnthndlr, managers):
        self.clnthndlr = clnthndlr
        self.managers = managers

    def _handle_reception(self, intial_data):
        data = self.clnthndlr.handle_receiving_data(intial_data)

        try:
            packet_id = data.packet_id

            for manager in self.managers:
                if manager.responds_to(packet_id):
                    manager.handle_request(self.clnthndlr, packet_id, data)
                    break

        except Exception as e:
            if str(e) == "[WinError 10035] A non-blocking socket operation could not be completed immediately":
                return

            if not str(e) == "[WinError 10054] An existing connection was forcibly closed by the remote host":
                log(e)
            self.clnthndlr.isConnected = False

    def init(self):
        pass

    def loop(self):
        self.clnthndlr.conn.setblocking(0)
        try:
            self._handle_reception(self.clnthndlr.receive_data(1))
        except socket.error as e:
            if str(e) == "[WinError 10035] A non-blocking socket operation could not be completed immediately":
                return

            if not str(e) == "[WinError 10054] An existing connection was forcibly closed by the remote host":
                log(e)
            self.clnthndlr.isConnected = False
        self.clnthndlr.conn.setblocking(1)
