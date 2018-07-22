import socket

from log import log
from socket_handler import Handler


class Client(Handler):
    cache = []

    def __init__(self, self_name=None, peer_name=None, conn=None, self_ip=None, self_port=None, peer_ip=None, peer_port=None, call_back=None, call_back_args=None):
        super().__init__(self_name=self_name, peer_name=peer_name, conn=conn, self_ip=self_ip, self_port=self_port, peer_ip=peer_ip, peer_port=peer_port, call_back=call_back, call_back_args=call_back_args)

        #TODO remove debug line
        self.log_coms = False

    @classmethod
    def __get_cache(cls, peer_ip):
        for o in Client.cache:
            if o.self_ip == peer_ip:
                return o
        return None

    @classmethod
    def create(cls, self_name=None, peer_name=None, conn=None, self_ip=None, self_port=None, peer_ip=None, peer_port=None, call_back=None, call_back_args=None):
        o = cls.__get_cache(peer_ip)
        if not o:
            o = cls(self_name=self_name, peer_name=peer_name, conn=conn, self_ip=self_ip, self_port=self_port, peer_ip=peer_ip, peer_port=peer_port, call_back=call_back, call_back_args=call_back_args)
            cls.cache.append(o)
        else:
            o.conn = conn
            o.self_ip = peer_ip
            o.self_port = peer_port
            o.isConnected = True
        return o


def init_socket(ip, port, connection_buffer_limit):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((ip, port))
    except socket.error as e:
        log(str(e))

    log("Bound to:", ip + ':' + str(port))

    s.listen(connection_buffer_limit)

    log("Listening on:", ip + ':' + str(port) + '\n')

    #s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    return s


def generate_handler(self_name=None, peer_name=None, conn=None, self_ip=None, self_port=None, peer_ip=None, peer_port=None, call_back=None, call_back_args=None):
    return Client.create(self_name=self_name, peer_name=peer_name, conn=conn, self_ip=self_ip, self_port=self_port, peer_ip=peer_ip, peer_port=peer_port, call_back=call_back, call_back_args=call_back_args)
