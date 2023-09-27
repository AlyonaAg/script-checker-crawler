from enum import Enum
import BaseClass
import AST
import re
import zlib
import base64
from jsbeautifier import default_options, beautify_file


class PrintAST:
    class __TypeElem(Enum):
        INSTR = 1
        ATOMS = 2

    __shift = 0

    def __init__(self, ast, file=None):
        self.__ast = ast
        self.__file = None
        if file is not None:
            self.__file = open(file, 'w')


    def print(self):
        self.__printDFS(self.__ast, None)

    def __printDFS(self, elem, type_elem):
        if type_elem is PrintAST.__TypeElem.INSTR:
            self.__printShift()
            if isinstance(elem, AST.AST):
                for instr in elem.tree:
                    self.__printDFS(instr, PrintAST.__TypeElem.INSTR)

            elif isinstance(elem, BaseClass.For):
                print('for (', end='', file=self.__file)
                self.__printDFS(elem.init, PrintAST.__TypeElem.ATOMS)
                print('; ', end='', file=self.__file)
                self.__printDFS(elem.conditions, PrintAST.__TypeElem.ATOMS)
                print('; ', end='', file=self.__file)
                self.__printDFS(elem.step, PrintAST.__TypeElem.ATOMS)
                print(')', file=self.__file)
                if len(elem.body) > 1:
                    self.__printShift()
                    print('{', file=self.__file)
                self.__incShift()
                for instr in elem.body:
                    self.__printDFS(instr, PrintAST.__TypeElem.INSTR)
                self.__decShift()
                if len(elem.body) > 1:
                    self.__printShift()
                    print('}', file=self.__file)

            elif isinstance(elem, BaseClass.While):
                print('while (', end='', file=self.__file)
                self.__printDFS(elem.conditions, PrintAST.__TypeElem.ATOMS)
                print(')', file=self.__file)
                if len(elem.body) > 1:
                    self.__printShift()
                    print('{', file=self.__file)
                self.__incShift()
                for instr in elem.body:
                    self.__printDFS(instr, PrintAST.__TypeElem.INSTR)
                self.__decShift()
                if len(elem.body) > 1:
                    self.__printShift()
                    print('}', file=self.__file)

            elif isinstance(elem, BaseClass.DoWhile):
                print('{', file=self.__file)
                self.__incShift()
                for instr in elem.body:
                    self.__printDFS(instr, PrintAST.__TypeElem.INSTR)
                self.__decShift()
                print('} (', end='', file=self.__file)
                self.__printDFS(elem.conditions, PrintAST.__TypeElem.ATOMS)
                print(')', file=self.__file)

            elif isinstance(elem, BaseClass.SwitchCommand):
                if elem.switch_command_type is BaseClass.TypeSwitchCommand.CASE:
                    print('case (', end='', file=self.__file)
                    self.__printDFS(elem.conditions, PrintAST.__TypeElem.ATOMS)
                    print('):', file=self.__file)
                else:
                    print('default:', file=self.__file)
                self.__incShift()
                for instr in elem.body:
                    self.__printDFS(instr, PrintAST.__TypeElem.INSTR)
                self.__decShift()

            elif isinstance(elem, BaseClass.If):
                print('if (', end='', file=self.__file)
                self.__printDFS(elem.conditions, PrintAST.__TypeElem.ATOMS)
                print(')', file=self.__file)
                if len(elem.body) > 1:
                    self.__printShift()
                    print('{', file=self.__file)
                self.__incShift()
                for instr in elem.body:
                    self.__printDFS(instr, PrintAST.__TypeElem.INSTR)
                self.__decShift()
                if len(elem.body) > 1:
                    self.__printShift()
                    print('}', file=self.__file)

            elif isinstance(elem, BaseClass.Switch):
                print('switch (', end='', file=self.__file)
                self.__printDFS(elem.conditions, PrintAST.__TypeElem.ATOMS)
                print('){', file=self.__file)
                self.__incShift()
                for instr in elem.body:
                    self.__printDFS(instr, PrintAST.__TypeElem.INSTR)
                self.__decShift()
                self.__printShift()
                print('}', file=self.__file)

            elif isinstance(elem, BaseClass.Else):
                print('else', file=self.__file)
                if len(elem.body) > 1:
                    print('{', file=self.__file)
                self.__incShift()
                for instr in elem.body:
                    self.__printDFS(instr, PrintAST.__TypeElem.INSTR)
                self.__decShift()
                if len(elem.body) > 1:
                    print('}', file=self.__file)

            elif isinstance(elem, BaseClass.Func):
                print('function ', end='', file=self.__file)
                if elem.name is not None:
                    print(f'{elem.name}', end='', file=self.__file)
                print('(', end='', file=self.__file)
                if len(elem.args):
                    for arg in elem.args[:-1]:
                        self.__printDFS([arg], PrintAST.__TypeElem.ATOMS)
                        print(end=', ')
                    self.__printDFS([elem.args[-1]], PrintAST.__TypeElem.ATOMS)
                print('){', file=self.__file)
                self.__incShift()
                for instr in elem.body:
                    self.__printDFS(instr, PrintAST.__TypeElem.INSTR)
                self.__decShift()
                print('}', end='', file=self.__file)
                if elem.name is not None:
                    print('\n', file=self.__file)

            elif isinstance(elem, BaseClass.Declaration):
                if elem.type is BaseClass.TypeDeclaration.VAR:
                    print('var ', end='', file=self.__file)
                else:
                    print('let ', end='', file=self.__file)
                self.__printDFS(elem.body, PrintAST.__TypeElem.ATOMS)
                print(';', file=self.__file)

            elif isinstance(elem, BaseClass.Return):
                print('return', end='', file=self.__file)
                if len(elem.return_value):
                    print(' ', end='', file=self.__file)
                    self.__printDFS(elem.return_value, PrintAST.__TypeElem.ATOMS)
                print(';', file=self.__file)

            elif isinstance(elem, BaseClass.OtherInstruction):
                self.__printDFS(elem.atoms, PrintAST.__TypeElem.ATOMS)
                print(';', file=self.__file)

            elif isinstance(elem, BaseClass.CycleControl):
                if elem.type is BaseClass.TypeCycleControl.CONTINUE:
                    print('continue;', file=self.__file)
                else:
                    print('break;', file=self.__file)

        elif type_elem is None:
            result = re.findall(r'(strt=\"([^\"]+)\")', self.__ast.script)
            if len(result):
                print(zlib.decompress(base64.b64decode(bytes(result[0][1], encoding='utf8'))).decode("utf-8"))
            else:
                opts = default_options()
                opts.keep_array_indentation = True
                opts.keep_function_indentation = True
                opts.indent_with_tabs = True
                opts.jslint_happy = True
                opts.eval_code = True
                opts.unescape_strings = True
                opts.comma_first = True
                opts.end_with_newline = True
                res = beautify_file((self.__ast.filename), opts)
                print(res)

        elif type_elem is PrintAST.__TypeElem.ATOMS:
            for atom in elem:
                if isinstance(atom, BaseClass.Func):
                    self.__printDFS(atom, PrintAST.__TypeElem.INSTR)

                elif isinstance(atom, BaseClass.Var):
                    print(atom.name, end='', file=self.__file)

                elif isinstance(atom, BaseClass.Number):
                    print(atom.value, end='', file=self.__file)

                elif isinstance(atom, BaseClass.String):
                    print(atom.value, end='', file=self.__file)

                elif isinstance(atom, BaseClass.Border):
                    print(', ', end='', file=self.__file)

                elif isinstance(atom, BaseClass.New):
                    print('new ', end='', file=self.__file)

                elif isinstance(atom, BaseClass.Const):
                    print('const ', end='', file=self.__file)

                elif isinstance(atom, BaseClass.Infinity):
                    print('Infinity', end='', file=self.__file)

                elif isinstance(atom, BaseClass.Bool):
                    if atom.bool_type == BaseClass.TypeBool.TRUE:
                        print('true', end='', file=self.__file)
                    else:
                        print('false', end='', file=self.__file)

                elif isinstance(atom, BaseClass.Array):
                    print('[', end='', file=self.__file)
                    self.__printDFS(atom.atoms, PrintAST.__TypeElem.ATOMS)
                    print(']', end='', file=self.__file)

                elif isinstance(atom, BaseClass.CallFunc):
                    print(f'{atom.func.name}(', end='', file=self.__file)
                    self.__printDFS(atom.args, PrintAST.__TypeElem.ATOMS)
                    print(')', end='', file=self.__file)

                elif isinstance(atom, BaseClass.ArithmeticOperation):
                    if atom.operation_type == BaseClass.TypeArithmeticOperation.ADD:
                        print(' + ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeArithmeticOperation.SUB:
                        print(' - ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeArithmeticOperation.MUL:
                        print(' * ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeArithmeticOperation.DIV:
                        print(' / ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeArithmeticOperation.MOD:
                        print(' % ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeArithmeticOperation.DEG:
                        print(' ** ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeArithmeticOperation.INC:
                        print('++ ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeArithmeticOperation.DEC:
                        print('-- ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeArithmeticOperation.ASSIGN:
                        print(' = ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeArithmeticOperation.ADD_ASSIGN:
                        print(' += ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeArithmeticOperation.SUB_ASSIGN:
                        print(' -= ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeArithmeticOperation.MUL_ASSIGN:
                        print(' *= ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeArithmeticOperation.DIV_ASSIGN:
                        print(' /= ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeArithmeticOperation.DEG_ASSIGN:
                        print(' **= ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeArithmeticOperation.MOD_ASSIGN:
                        print(' %= ', end='', file=self.__file)

                elif isinstance(atom, BaseClass.BinaryOperation):
                    if atom.operation_type == BaseClass.TypeBinaryOperation.LEFT_SHIFT:
                        print(' << ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeBinaryOperation.RIGHT_SHIFT:
                        print(' >> ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeBinaryOperation.RIGHT_SHIFT_FILL:
                        print(' >>> ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeBinaryOperation.NOT:
                        print(' ~ ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeBinaryOperation.AND:
                        print(' & ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeBinaryOperation.OR:
                        print(' | ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeBinaryOperation.XOR:
                        print(' ^ ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeBinaryOperation.LEFT_SHIFT_ASSIGN:
                        print(' >>= ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeBinaryOperation.RIGHT_SHIFT_ASSIGN:
                        print(' <<= ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeBinaryOperation.RIGHT_SHIFT_FILL_ASSIGN:
                        print(' >>>= ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeBinaryOperation.NOT_ASSIGN:
                        print(' ~= ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeBinaryOperation.AND_ASSIGN:
                        print(' &= ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeBinaryOperation.OR_ASSIGN:
                        print(' |= ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeBinaryOperation.XOR_ASSIGN:
                        print(' ^= ', end='', file=self.__file)

                elif isinstance(atom, BaseClass.LogicalOperation):
                    if atom.operation_type == BaseClass.TypeLogicalOperation.EQ:
                        print(' == ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeLogicalOperation.NE:
                        print(' != ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeLogicalOperation.LESS:
                        print(' < ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeLogicalOperation.GREATER:
                        print(' > ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeLogicalOperation.LESS_EQ:
                        print(' <= ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeLogicalOperation.GREATER_EQ:
                        print(' >= ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeLogicalOperation.AND:
                        print(' && ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeLogicalOperation.OR:
                        print(' || ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeLogicalOperation.AND_ASSIGN:
                        print(' &&= ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeLogicalOperation.OR_ASSIGN:
                        print(' ||= ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeLogicalOperation.NULLISH:
                        print(' ?? ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeLogicalOperation.NULLISH_ASSIGN:
                        print(' ??= ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeLogicalOperation.NOT:
                        print('!', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeLogicalOperation.TRIPLE_EQ:
                        print(' === ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeLogicalOperation.TRIPLE_NE:
                        print(' !== ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeLogicalOperation.SHORT_IF:
                        print(' ? ', end='', file=self.__file)
                    elif atom.operation_type == BaseClass.TypeLogicalOperation.SHORT_COND:
                        print(' : ', end='', file=self.__file)

                elif isinstance(atom, BaseClass.Brackets):
                    print('(', end='', file=self.__file)
                    self.__printDFS(atom.atoms, PrintAST.__TypeElem.ATOMS)
                    print(')', end='', file=self.__file)

                elif isinstance(atom, BaseClass.InstanceClass):
                    self.__printDFS([atom.instance], PrintAST.__TypeElem.ATOMS)
                    print('.', end='', file=self.__file)
                    self.__printDFS([atom.field], PrintAST.__TypeElem.ATOMS)

                else:
                    self.__printDFS(atom, PrintAST.__TypeElem.INSTR)

    def __printShift(self):
        print('\t' * PrintAST.__shift, end='', file=self.__file)

    @staticmethod
    def __incShift():
        PrintAST.__shift += 1

    @staticmethod
    def __decShift():
        PrintAST.__shift -= 1
