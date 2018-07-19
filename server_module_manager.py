import json
from queue import Queue

import manager
import packet
import server_module_packager as mp
from log import log


class ModuleManager(manager.Manager):

    def __init__(self, clnthndlr):
        self.clnthndlr = clnthndlr
        self.module = None

    def _export_module_data(self, module_data):
        pk = packet.Packet(module_data, packet.PACKET_ID_FUNC_INIT)
        self.clnthndlr.send_packet(pk)

    def _func_call_return_value(self, return_data):
        pk = packet.Packet(str(return_data), packet.PACKET_ID_FUNC_CALL_RETURN)
        self.clnthndlr.send_packet(pk)

    def _func_call_return_error(self, error_info):
        pk = packet.Packet((str(dict(data=error_info))), packet.PACKET_ID_FUNC_CALL_ERROR)
        self.clnthndlr.send_packet(pk)

    def handle_request(self, clnthndlr, packet_id, data):
        try:
            if packet_id is packet.PACKET_ID_FUNC_INIT:
                # Module Handler
                formatted_modue_export = mp.format_module_export(self.module)
                self._export_module_data(formatted_modue_export)
            elif packet_id is packet.PACKET_ID_FUNC_CALL:
                data = json.loads(data.get_data())

                host_cls = data["host_cls"]
                func_type = int(data["func_type"])
                func_name = data["name"]
                func_args = list(data["args"])

                result = None

                if func_type == mp.FUNC_TYPE.MODULE_FUNC.value:
                    result = mp.exec_func(self.module, func_name, *func_args)
                elif func_type == mp.FUNC_TYPE.INSTANCE_FUNC.value:
                    # TODO resolve instance methods
                    # cls_instance = cls()
                    # method = getattr(cls_instance, func_name)
                    # result = method(*func_args)
                    result = "INSTANCE_METHODS ARE NOT SUPPORTED ATM"
                elif func_type == mp.FUNC_TYPE.CLASS_FUNC.value:
                    cls = mp.get_class(self.module, host_cls)
                    result = mp.exec_func(cls, func_name, *func_args)
                elif func_type == mp.FUNC_TYPE.PROPERTY_FUNC.value:
                    # TODO resolve property methods
                    result = "PROPERTY_METHODS ARE NOT SUPPORTED ATM"
                elif func_type == mp.FUNC_TYPE.STATIC_FUNC.value:
                    cls = mp.get_class(self.module, host_cls)
                    result = mp.exec_func(cls, func_name, *func_args)

                    self._func_call_return_value(result)
        except Exception as e:
            log(e)
            self._func_call_return_error(str(e))
            raise e

    def init(self):
        self.module = mp.load_module("secretmath")

    def loop(self):
        pass

    def responds_to(self, packet_id):
        return 0 <= packet_id < 100
