import Parser


class AST:
    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.__script = f.read()
        self.__Tree = []
        self.filename = filename

    @property
    def tree(self):
        return self.__Tree

    @property
    def script(self):
        return self.__script

    def createAST(self):
        parser = Parser.Parser()
        self.__Tree = parser.parserAST(self.__script)
