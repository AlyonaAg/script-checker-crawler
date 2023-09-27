from enum import Enum


# interface (Instruction and Atom)
class Instruction:
    def print(self):
        pass


class Atom:
    def print(self):
        pass


# base enum
class TypeDeclaration(Enum):
    VAR = 1
    LET = 2


class TypeCycleControl(Enum):
    CONTINUE = 1
    BREAK = 2


class TypeSwitchCommand(Enum):
    CASE = 1
    DEFAULT = 2


class TypeBool(Enum):
    TRUE = 1
    FALSE = 2


class TypeArithmeticOperation(Enum):
    ADD = 1
    SUB = 2
    MUL = 3
    DIV = 4
    MOD = 5
    DEG = 6
    INC = 7
    DEC = 8
    ASSIGN = 9
    ADD_ASSIGN = 10
    SUB_ASSIGN = 11
    MUL_ASSIGN = 12
    DIV_ASSIGN = 13
    DEG_ASSIGN = 14
    MOD_ASSIGN = 15


class TypeBinaryOperation(Enum):
    LEFT_SHIFT = 1
    RIGHT_SHIFT = 2
    RIGHT_SHIFT_FILL = 3  # >>>
    NOT = 4  # ~
    AND = 5
    OR = 6
    XOR = 7
    LEFT_SHIFT_ASSIGN = 8
    RIGHT_SHIFT_ASSIGN = 9
    RIGHT_SHIFT_FILL_ASSIGN = 10  # >>>=
    NOT_ASSIGN = 11
    AND_ASSIGN = 12
    OR_ASSIGN = 13
    XOR_ASSIGN = 14


class TypeLogicalOperation(Enum):
    EQ = 1  # ==
    NE = 2  # !=
    LESS = 3  # <
    GREATER = 4  # >
    LESS_EQ = 5  # <=
    GREATER_EQ = 6  # >=
    AND = 7
    OR = 8
    AND_ASSIGN = 9
    OR_ASSIGN = 10
    NULLISH = 11  # ??
    NULLISH_ASSIGN = 12  # ??=
    NOT = 13
    TRIPLE_EQ = 14  # ===
    TRIPLE_NE = 15  # !==
    SHORT_IF = 16  # ?
    SHORT_COND = 17  # :


# base instruction
class Func(Instruction):
    def __init__(self, name, args=[], body=[]):
        self.name = name
        self.args = args
        self.body = body
        self.cnt_reference = 0

    def inc(self):
        self.cnt_reference += 1


class Declaration(Instruction):
    def __init__(self, declaration_type, body=[]):
        self.body = body
        self.type = declaration_type


class CycleControl(Instruction):
    def __init__(self, type_cycle_control):
        self.type = type_cycle_control


class Return(Instruction):
    def __init__(self, return_value=None):
        self.return_value = return_value


class While(Instruction):
    def __init__(self, conditions, body):
        self.conditions = conditions
        self.body = body


class If(Instruction):
    def __init__(self, conditions, body):
        self.conditions = conditions
        self.body = body


class Else(Instruction):
    def __init__(self, body):
        self.body = body


class For(Instruction):
    def __init__(self, init, conditions, step, body):
        self.init = init
        self.conditions = conditions
        self.step = step
        self.body = body


class Switch(Instruction):
    def __init__(self, conditions, body):
        self.conditions = conditions
        self.body = body


class DoWhile(Instruction):
    def __init__(self, conditions, body):
        self.conditions = conditions
        self.body = body


class SwitchCommand(Instruction):
    def __init__(self, switch_command_type, conditions, body):
        self.switch_command_type = switch_command_type
        self.conditions = conditions
        self.body = body


class OtherInstruction(Instruction):
    def __init__(self, atoms):
        self.atoms = atoms


# base atom
class Var(Atom):
    def __init__(self, name, namespace='__main', value=None):
        self.name = name
        self.namespace = namespace
        self.value = value


class Number(Atom):
    def __init__(self, value):
        self.value = value


class String(Atom):
    def __init__(self, value):
        self.value = value


class Array(Atom):
    def __init__(self, atoms):
        self.atoms = atoms


class CallFunc(Atom):
    def __init__(self, func, args):
        self.func = func
        self.args = args


class Bool(Atom):
    def __init__(self, bool_type):
        self.bool_type = bool_type


class ArithmeticOperation(Atom):
    def __init__(self, operation_type):
        self.operation_type = operation_type


class BinaryOperation(Atom):
    def __init__(self, operation_type):
        self.operation_type = operation_type


class LogicalOperation(Atom):
    def __init__(self, operation_type):
        self.operation_type = operation_type


class Border(Atom):
    def __init__(self):
        pass


class Brackets(Atom):
    def __init__(self, atoms):
        self.atoms = atoms


class New(Atom):
    def __init__(self):
        pass


class InstanceClass(Atom):
    def __init__(self, instance, field):
        self.instance = instance
        self.field = field


class Const(Atom):
    def __init__(self):
        pass


class Infinity(Atom):
    def __init__(self):
        pass
