import BaseClass
import Repository
import AST
import Parser
from enum import Enum


class ProcessingAST:
    class __TypeElem(Enum):
        INSTR = 1
        ATOMS = 2

    def __init__(self, ast):
        self.__ast = ast

    @property
    def ast(self):
        return self.__ast

    def processing(self):
        self.__deleteUnusedFunction()
        self.__renameVar()
        self.__renameFunc()
        # self.__arithmeticSimplification(self.__ast, ProcessingAST.__TypeElem.INSTR)

    def __deleteUnusedFunction(self):
        del_instr = []
        for instr in self.__ast.tree:
            if isinstance(instr, BaseClass.Func) and not instr.cnt_reference:
                del_instr.append(instr)
        for instr in del_instr:
            self.__ast.tree.remove(instr)

    def __arithmeticSimplification(self, elem, type_elem):
        if type_elem is ProcessingAST.__TypeElem.INSTR:
            self.__removeDeadCode(elem)
            self.__replaceCall(elem)
            if isinstance(elem, AST.AST):
                for instr in elem.tree:
                    self.__arithmeticSimplification(instr, ProcessingAST.__TypeElem.INSTR)
            elif isinstance(elem, BaseClass.For):
                self.__arithmeticSimplification(elem.init, ProcessingAST.__TypeElem.ATOMS)
                self.__arithmeticSimplification(elem.conditions, ProcessingAST.__TypeElem.ATOMS)
                self.__arithmeticSimplification(elem.step, ProcessingAST.__TypeElem.ATOMS)
                for instr in elem.body:
                    self.__arithmeticSimplification(instr, ProcessingAST.__TypeElem.INSTR)
            elif isinstance(elem, BaseClass.While):
                self.__arithmeticSimplification(elem.conditions, ProcessingAST.__TypeElem.ATOMS)
                for instr in elem.body:
                    self.__arithmeticSimplification(instr, ProcessingAST.__TypeElem.INSTR)
            elif isinstance(elem, BaseClass.DoWhile):
                self.__arithmeticSimplification(elem.conditions, ProcessingAST.__TypeElem.ATOMS)
                for instr in elem.body:
                    self.__arithmeticSimplification(instr, ProcessingAST.__TypeElem.INSTR)
            elif isinstance(elem, BaseClass.SwitchCommand):
                self.__arithmeticSimplification(elem.conditions, ProcessingAST.__TypeElem.ATOMS)
                for instr in elem.body:
                    self.__arithmeticSimplification(instr, ProcessingAST.__TypeElem.INSTR)
            elif isinstance(elem, BaseClass.If):
                self.__arithmeticSimplification(elem.conditions, ProcessingAST.__TypeElem.ATOMS)
                for instr in elem.body:
                    self.__arithmeticSimplification(instr, ProcessingAST.__TypeElem.INSTR)
            elif isinstance(elem, BaseClass.Switch):
                self.__arithmeticSimplification(elem.conditions, ProcessingAST.__TypeElem.ATOMS)
                for instr in elem.body:
                    self.__arithmeticSimplification(instr, ProcessingAST.__TypeElem.INSTR)
            elif isinstance(elem, BaseClass.Else):
                for instr in elem.body:
                    self.__arithmeticSimplification(instr, ProcessingAST.__TypeElem.INSTR)
            elif isinstance(elem, BaseClass.Func):
                for instr in elem.body:
                    self.__arithmeticSimplification(instr, ProcessingAST.__TypeElem.INSTR)
            elif isinstance(elem, BaseClass.Declaration):
                self.__arithmeticSimplification(elem.body, ProcessingAST.__TypeElem.ATOMS)
            elif isinstance(elem, BaseClass.Return):
                self.__arithmeticSimplification(elem.return_value, ProcessingAST.__TypeElem.ATOMS)
            elif isinstance(elem, BaseClass.OtherInstruction):
                self.__arithmeticSimplification(elem.atoms, ProcessingAST.__TypeElem.ATOMS)
        elif type_elem is ProcessingAST.__TypeElem.ATOMS:
            self.__searchArithSignature(elem)
            for atom in elem:
                if isinstance(atom, BaseClass.InstanceClass):
                    if isinstance(atom.instance, BaseClass.CallFunc):
                        self.__arithmeticSimplification(atom.instance.args, ProcessingAST.__TypeElem.ATOMS)
                    if isinstance(atom.field, BaseClass.CallFunc):
                        self.__arithmeticSimplification(atom.field.args, ProcessingAST.__TypeElem.ATOMS)
                    if isinstance(atom.field, BaseClass.InstanceClass) and \
                            isinstance(atom.field.instance, BaseClass.CallFunc):
                        self.__arithmeticSimplification(atom.field.instance.args, ProcessingAST.__TypeElem.ATOMS)

                if isinstance(atom, BaseClass.Brackets):
                    self.__arithmeticSimplification(atom.atoms, ProcessingAST.__TypeElem.ATOMS)
                if isinstance(atom, BaseClass.Array):
                    self.__arithmeticSimplification(atom.atoms, ProcessingAST.__TypeElem.ATOMS)
                if isinstance(atom, BaseClass.Func):
                    self.__arithmeticSimplification(atom, ProcessingAST.__TypeElem.INSTR)
                if isinstance(atom, BaseClass.CallFunc):
                    if atom.func.name == 'eval':
                        self.__replaceEval(elem)
                        for a in elem:
                            self.__arithmeticSimplification(a, ProcessingAST.__TypeElem.INSTR)
                    else:
                        self.__arithmeticSimplification(atom.args, ProcessingAST.__TypeElem.ATOMS)
            self.__searchEmptyBrackets(elem)

    def __searchArithSignature(self, atoms):
        if len(atoms) < 3:
            return

        prior_operation = [BaseClass.TypeArithmeticOperation.DEG,
                           BaseClass.TypeArithmeticOperation.MUL,
                           BaseClass.TypeArithmeticOperation.DIV,
                           BaseClass.TypeArithmeticOperation.MOD,
                           BaseClass.TypeArithmeticOperation.ADD,
                           BaseClass.TypeArithmeticOperation.SUB,
                           BaseClass.TypeBinaryOperation.LEFT_SHIFT,
                           BaseClass.TypeBinaryOperation.RIGHT_SHIFT,
                           BaseClass.TypeBinaryOperation.AND,
                           BaseClass.TypeBinaryOperation.XOR,
                           BaseClass.TypeBinaryOperation.OR]

        for op in prior_operation:
            i = 0
            while i < len(atoms) - 2:
                if isinstance(atoms[i], BaseClass.Number) and \
                        (isinstance(atoms[i + 1], BaseClass.ArithmeticOperation) or
                         isinstance(atoms[i + 1], BaseClass.BinaryOperation)) and \
                        isinstance(atoms[i + 2], BaseClass.Number):
                    if not self.__replaceSignature(atoms, i, op):
                        i = 0
                i += 1

    def __searchEmptyBrackets(self, atoms):
        if not len(atoms):
            return

        i = 0
        while i < len(atoms):
            if isinstance(atoms[i], BaseClass.Brackets):
                if len(atoms[i].atoms) == 1:
                    self.__deleteBrackets(atoms, i)
            i += 1

    def __replaceEval(self, atoms):
        for index, elem in enumerate(atoms):
            if isinstance(elem, BaseClass.CallFunc) and elem.func.name == 'eval':
                args = elem.args[0].value
                args = args[1:-1]
                if args.startswith('(') and args.endswith(')'):
                    args = args[1:-1]
                args = args.replace('\\"', '"')
                args = args.replace('\\\'', '\'')

                parser = Parser.Parser()
                new_instr = parser.parserAST(args)

                for instr in new_instr[::-1]:
                    atoms.pop(index)
                    atoms.insert(index, instr)
                break

    def __removeDeadCode(self, elem):
        conditions = []
        alwaysTrue = False

        if isinstance(elem, BaseClass.If):
            conditions = self.__splitOperation(elem.conditions)
        elif isinstance(elem, BaseClass.For):
            conditions = self.__splitOperation(elem.conditions)
        elif isinstance(elem, BaseClass.While):
            conditions = self.__splitOperation(elem.conditions)
        elif isinstance(elem, BaseClass.DoWhile):
            conditions = self.__splitOperation(elem.conditions)
        
        for cond in conditions:
            if len(cond) == 3:
                if self.__checkAlwaysTrueOperation():
                    alwaysTrue = True
                    break
            
        if alwaysTrue:
            elem = []


    def __replaceCall(self, elem):
        if isinstance(elem, BaseClass.Func):
            for e in elem.body:
                if isinstance(e, BaseClass.Return) and len(e.return_value) > 1:
                    if isinstance(e.return_value[1], BaseClass.Number) or \
                        isinstance(e.return_value[1], BaseClass.String):
                            return
                            self.__replaceAllReferences(elem.name)

    
    def __fillVarValue():
        pass 


    @staticmethod
    def __checkAlwaysTrueOperation(operation1, operation_type=None, operation2=None):
        if operation_type is None and operation2 is None:
            if operation1 == BaseClass.TypeBool.TRUE or \
               (isinstance(operation1, BaseClass.Number) and operation1.value) or \
                isinstance(operation1, BaseClass.String):
                return True
        else:
            if (operation1.value == operation2.value and 
                    isinstance(operation_type, BaseClass.TypeLogicalOperation.EQ)) or \
                (operation1.value != operation2.value and 
                    isinstance(operation_type, BaseClass.TypeLogicalOperation.NE)) or \
                (operation1.value < operation2.value and 
                    isinstance(operation_type, BaseClass.TypeLogicalOperation.LESS)) or \
                (operation1.value > operation2.value and 
                    isinstance(operation_type, BaseClass.TypeLogicalOperation.GREATER)) or \
                (operation1.value <= operation2.value and 
                    isinstance(operation_type, BaseClass.TypeLogicalOperation.LESS_EQ)) or \
                (operation1.value >= operation2.value and 
                    isinstance(operation_type, BaseClass.TypeLogicalOperation.GREATER_EQ)):
                return True

        return False
        

    @staticmethod
    def __splitOperation(condition):
        conditions = []
        tempCondition = []

        for elem in condition:
            if isinstance(elem, BaseClass.TypeLogicalOperation.AND) or \
               isinstance(elem, BaseClass.TypeLogicalOperation.OR):
                conditions.append(tempCondition)
                tempCondition = []
                continue
            tempCondition.append(elem)

        return conditions


    @staticmethod
    def __replaceSignature(atoms, index, type_operation):
        if atoms[index + 1].operation_type is type_operation:
            if type_operation is BaseClass.TypeArithmeticOperation.DEG:
                new_number = BaseClass.Number(atoms[index].value ** atoms[index + 2].value)
            elif type_operation is BaseClass.TypeArithmeticOperation.MUL:
                new_number = BaseClass.Number(atoms[index].value * atoms[index + 2].value)
            elif type_operation is BaseClass.TypeArithmeticOperation.DIV:
                new_number = BaseClass.Number(atoms[index].value / atoms[index + 2].value)
            elif type_operation is BaseClass.TypeArithmeticOperation.MOD:
                new_number = BaseClass.Number(atoms[index].value % atoms[index + 2].value)
            elif type_operation is BaseClass.TypeArithmeticOperation.ADD:
                new_number = BaseClass.Number(atoms[index].value + atoms[index + 2].value)
            elif type_operation is BaseClass.TypeArithmeticOperation.SUB:
                new_number = BaseClass.Number(atoms[index].value - atoms[index + 2].value)
            elif type_operation is BaseClass.TypeBinaryOperation.LEFT_SHIFT:
                new_number = BaseClass.Number(atoms[index].value << atoms[index + 2].value)
            elif type_operation is BaseClass.TypeBinaryOperation.RIGHT_SHIFT:
                new_number = BaseClass.Number(atoms[index].value >> atoms[index + 2].value)
            elif type_operation is BaseClass.TypeBinaryOperation.AND:
                new_number = BaseClass.Number(atoms[index].value & atoms[index + 2].value)
            elif type_operation is BaseClass.TypeBinaryOperation.XOR:
                new_number = BaseClass.Number(atoms[index].value ^ atoms[index + 2].value)
            elif type_operation is BaseClass.TypeBinaryOperation.OR:
                new_number = BaseClass.Number(atoms[index].value | atoms[index + 2].value)
            atoms.pop(index)
            atoms.pop(index)
            atoms.pop(index)
            atoms.insert(index, new_number)
            return 0
        return 1

    @staticmethod
    def __deleteBrackets(atoms, index):
        atoms.insert(index, atoms[index].atoms[0])
        atoms.pop(index + 1)

    @staticmethod
    def __renameVar():
        repo = Repository.Repository()
        list_vars = repo.get_vars()
        for i, var in enumerate(list_vars):
            var.name = 'var' + str(i)

    @staticmethod
    def __renameFunc():
        repo = Repository.Repository()
        list_func = repo.get_funcs()
        for i, func in enumerate(list_func):
            func.name = 'function' + str(i)
