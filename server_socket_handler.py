import socket
import threading
from queue import Queue

import packet
import pthread
from log import log

server_name = "SERVER"

SHOW_SOCKET_COMS = True

class Client:
    cache = []

    def __init__(self, host=None, port=None, client_name=None, conn=None, addr=None, call_back=None, call_back_args=None):
        self.isConnected = True;
        self.host = host
        self.port = port
        self.client_name = client_name
        self.connection = conn
        self.address = addr
        self.call_back = call_back
        self.call_back_args = call_back_args
        self.outgoing_packet_queue = Queue()

    @classmethod
    def __get_cache(cls, addr):
        for o in Client.cache:
            if o.address[0] == addr[0] and o.address[1] == addr[1]:
                return o
        return None

    @classmethod
    def create(cls, host=None, port=None, client_name=None, conn=None, addr=None, call_back=None, call_back_args=None):
        o = cls.__get_cache(addr)
        if not o:
            o = cls(host=host, port=port, client_name=client_name, conn=conn, addr=addr, call_back=call_back, call_back_args=call_back_args)
            cls.cache.append(o)
        else:
            o.connection = conn
            o.addr = addr
            o.isConnected = True
        return o

    # sends packet to connection
    def _send_packet(self, packet):
        self.connection.sendall(packet.export())

    # receives a packet from client and adds it to a queue
    def _receive_packet(self, buffer_length):
        return packet.Packet(self.connection.recv(buffer_length))

    def _receive_data(self, buffer_length):
        return self.connection.recv(buffer_length)

    def send_all(self):
        while not self.outgoing_packet_queue.empty():
            self._send_packet(self.outgoing_packet_queue.get())

    def schedule_outgoing_packet(self, packet):
        self.outgoing_packet_queue.put(packet)

    # wrapper for packet sending
    def send_packet(self, packet):
        self.schedule_outgoing_packet(packet)
        if SHOW_SOCKET_COMS:
            log("<%s>" % server_name, packet, '\n')

    # wrapper for packet receiving
    def receive_packet(self, buffer_length):
        packet = self._receive_packet(buffer_length)
        if SHOW_SOCKET_COMS:
            log("<%s>" % self.client_name, packet, '\n')
        return packet

    def receive_data(self, buffer_length):
        return self._receive_data(buffer_length)

    def handle_receiving_data(self, initial_data):
        data = initial_data.decode('utf8')
        while len(data) < len(packet.STREAM_TERMINATING_BYTE) or data[-len(
                packet.STREAM_TERMINATING_BYTE):] != packet.STREAM_TERMINATING_BYTE.decode(
            'utf8'):
            data += self.receive_data(1).decode('utf8')

        data = data[:-len(packet.STREAM_TERMINATING_BYTE)]
        data = packet.Packet(str.encode(data))

        if SHOW_SOCKET_COMS:
            log("<%s>" % self.client_name, data, '\n')

        return data

    def handle_connection(self):
        thread = pthread.PThread(self.call_back, (self, *self.call_back_args), is_daemon=False)
        thread.start()
        return thread

    def print_connection_info(self):
        log('\n\nconnected to:', self.address[0] + ":" + str(self.address[1]))

    def print_disconnection_info(self):
        log(self.address[0] + ":" + str(self.address[1]), "disconnected\n\n")

    def disconnect(self):
        self.connection.shutdown(socket.SHUT_WR)


def init_socket(host, port, connection_buffer_limit):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((host, port))
    except socket.error as e:
        log(str(e))

    log("Bound to:", host + ':' + str(port))

    s.listen(connection_buffer_limit)

    log("Listening on:", host + ':' + str(port) + '\n')

    return s


def generate_client_handler(host=None, port=None, client_name=None, conn=None, addr=None, call_back=None, call_back_args=None):
    return Client.create(host=host, port=port, client_name=client_name, conn=conn, addr=addr, call_back=call_back, call_back_args=call_back_args)


def set_server_name(name):
    global server_name

    server_name = name
