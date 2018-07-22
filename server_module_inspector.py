import inspect
from enum import Enum

import inspect_mate

FUNC_TYPE = Enum("FUNC_TYPE", "MODULE_FUNC INSTANCE_FUNC CLASS_FUNC PROPERTY_FUNC STATIC_FUNC")


class ModuleInfo:
    __slots__ = ['module', 'cls_names', 'cls_func_names', 'cls_func_types', 'cls_func_args', 'func_names', 'func_args']

    def __init__(self, module):
        self.module = module
        self.cls_names, self.cls_func_names, self.cls_func_types, self.cls_func_args = self._get_class_info()
        self.func_names, self.func_args = self._get_func_info()

    def _get_func_info(self, copy_private=False):
        func_names, funcs = [], []

        module_functions_pairs = inspect.getmembers(self.module, inspect.isfunction)

        for funcPair in module_functions_pairs:
            name = funcPair[0]
            func = funcPair[1]

            if name[:1] != '_' or copy_private:
                args_pair = list(inspect.signature(func).parameters.items())
                args = []
                for arg in args_pair:
                    args.append(str(arg[1]))

                func_names.append(name)
                funcs.append(args)

        return func_names, funcs

    def _get_class_info(self, copy_private=False):
        cls_names = []
        func_names, func_types, func_args = [[]], [[]], [[]]

        cls_pairs = inspect.getmembers(self.module, inspect.isclass)
        func_pairs = []

        for clsPair in cls_pairs:
            name = clsPair[0]
            cls = clsPair[1]
            cls_names.append(name)

            func_pairs.append(inspect.getmembers(cls, inspect.isfunction))

        for clsIndex, clsFuncPair in enumerate(func_pairs):
            for funcPair in clsFuncPair:
                cls = cls_pairs[clsIndex][1]
                name = funcPair[0]
                func = funcPair[1]

                if name[:1] != '_' or copy_private:
                    args_pair = list(inspect.signature(func).parameters.items())
                    args = []
                    for arg in args_pair:
                        args.append(str(arg[1]))

                    func_type = None

                    if inspect_mate.is_regular_method(cls, name):
                        func_type = FUNC_TYPE.INSTANCE_FUNC.value
                    elif inspect_mate.is_class_method(cls, name):
                        func_type = FUNC_TYPE.CLASS_FUNC.value
                    elif inspect_mate.is_property_method(cls, name):
                        func_type = FUNC_TYPE.PROPERTY_FUNC.value
                    elif inspect_mate.is_static_method(cls, name):
                        func_type = FUNC_TYPE.STATIC_FUNC.value

                    func_names[clsIndex].append(name)
                    func_types[clsIndex].append(func_type)
                    func_args[clsIndex].append(args)

        return cls_names, func_names, func_types, func_args

    def get_class_names(self):
        return self.cls_names

    def get_class_func_names(self):
        return self.cls_func_names

    def get_class_func_types(self):
        return self.cls_func_types

    def get_class_func_args(self):
        return self.cls_func_args

    def get_func_names(self):
        return self.func_names

    def get_func_args(self):
        return self.cls_func_args

    def get_info(self):
        return self.cls_names, self.cls_func_names, self.cls_func_types, self.cls_func_args, self.func_names, self.func_args
