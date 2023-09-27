from GeneralDB import VarDB, FuncDB


class Repository:
    def __init__(self):
        self.__VarDB = VarDB.get_instance()
        self.__FuncDB = FuncDB.get_instance()

    def get_vars(self):
        return self.__VarDB.vars

    def get_funcs(self):
        return self.__FuncDB.funcs

    def append_var(self, value):
        self.__VarDB.append(value)

    def append_func(self, value):
        self.__FuncDB.append(value)

    def search_var(self, name):
        for var in self.__VarDB.vars:
            if name == var.name:
                return var
        return None

    def search_func(self, name):
        for func in self.__FuncDB.funcs:
            if name == func.name:
                func.inc()
                return func

