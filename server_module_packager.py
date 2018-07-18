import json

import server_module_inspector as mi

FUNC_TYPE = mi.FUNC_TYPE


def load_module(module_name):
    module = __import__(module_name)

    return module


def get_class(module, class_name):
    cls = getattr(module, class_name)
    return cls


def get_instance(module, class_name):
    cls = getattr(module, class_name)
    return cls()


def exec_func(obj, func_name, *args):
    func = getattr(obj, func_name)
    return func(*args)


def construct_json(module):
    result = ''

    module_info = mi.ModuleInfo(module)
    cls_names, cls_func_names, cls_func_types, cls_func_args, func_names, func_args = module_info.get_info()

    data = dict()

    data["name"] = module.__name__
    data["classes"] = dict()
    data["functions"] = dict()

    for class_index, cls in enumerate(cls_names):
        data["classes"][cls] = dict()
        data["classes"][cls]["name"] = cls
        data["classes"][cls]["functions"] = dict()
        for func_index, func in enumerate(cls_func_names[class_index]):
            data["classes"][cls]["functions"][func] = dict()
            data["classes"][cls]["functions"][func]["name"] = func
            data["classes"][cls]["functions"][func]["type"] = cls_func_types[class_index][func_index]
            data["classes"][cls]["functions"][func]["args"] = cls_func_args[class_index][func_index]

    for func_index, func in enumerate(func_names):
        data["functions"][func] = dict()
        data["functions"][func]["name"] = func
        data["functions"][func]["type"] = mi.FUNC_TYPE.MODULE_FUNC.value
        data["functions"][func]["args"] = func_args[func_index]

    result = json.dumps(data, sort_keys=False)
    return result


def format_module_export(module):
    return construct_json(module)
