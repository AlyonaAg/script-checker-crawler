class VarDB:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = VarDB()
        return cls._instance

    def __init__(self):
        self.__vars = list()

    @property
    def vars(self):
        return self.__vars

    def append(self, value):
        self.__vars += value


class FuncDB:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = FuncDB()
        return cls._instance

    def __init__(self):
        self.__funcs = list()

    @property
    def funcs(self):
        return self.__funcs

    def append(self, value):
        self.__funcs.append(value)
