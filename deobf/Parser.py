import re
import Repository
import BaseClass


class Parser:
    __namespace = '__main'

    def parserAST(self, script):
        instrAST = []
        i = 0
        while i < len(script):
            instr, shift = self.__getInstruction(script[i:])

            if instr is not None:
                instrAST.append(instr)
                i += shift - 1
            i += 1
        return instrAST

    def __parserFunc(self, script):
        start = re.search(r'(\{)', script).start()
        finish = start + self.__searchForBoundaries(script[start + 1:], '[{]', '[}]') + 1
        declaration = re.match(r'function ([a-zA-Z_]\w+)\((.*?)\)', script)

        if declaration is not None:
            name = declaration.group(1)
        else:
            name = declaration
        Parser.__namespace = name

        args = []
        repo = Repository.Repository()
        if declaration is not None:
            for arg in declaration.group(2).split(sep=','):
                if (var := repo.search_var(arg)) is None:
                    var = BaseClass.Var(arg, Parser.__namespace)
                    repo.append_var([var])
                args.append(var)
        else:
            args = []

        body = []
        if (func := repo.search_func(name)) is not None:
            func.body = body
        else:
            func = BaseClass.Func(name, args, body)

        if func.name is not None:
            repo.append_func(func)

        i = start
        while i < finish:
            instr, shift = self.__getInstruction(script[i:])
            if instr is not None:
                i += shift - 1
                body.append(instr)
            i += 1

        Parser.__namespace = "__main"
        return func, finish

    def __parserDeclaration(self, script):
        declaration_type = BaseClass.TypeDeclaration.VAR if script[:3] == 'var' else BaseClass.TypeDeclaration.LET
        finish = self.__searchEndOfCommand(script) + 1

        body = self.__getAtomList(script[3:finish])
        return BaseClass.Declaration(declaration_type, body), finish

    def __parserCycleControl(self, script):
        cycle_control_type = BaseClass.TypeCycleControl.CONTINUE if script.startswith(
            'continue') else BaseClass.TypeCycleControl.BREAK
        finish = self.__searchEndOfCommand(script) + 1

        return BaseClass.CycleControl(cycle_control_type), finish

    def __parserReturn(self, script):
        start_return_value = len('return')
        finish_return_value = self.__searchEndOfCommand(script) + 1
        return_value = self.__getAtomList(script[start_return_value:finish_return_value])
        return BaseClass.Return(return_value), finish_return_value

    def __parserWhile(self, script):
        start_conditions = re.search(r'(\()', script).start() + 1
        finish_conditions = start_conditions + self.__searchForBoundaries(script[start_conditions:], '[(]', '[)]')
        condition = self.__getAtomList(script[start_conditions:finish_conditions])
        body, i = self.__getBody(script, finish_conditions)
        return BaseClass.While(condition, body), i

    def __parserIf(self, script):
        start_conditions = re.search(r'(\()', script).start() + 1
        finish_conditions = start_conditions + self.__searchForBoundaries(script[start_conditions:], '[(]', '[)]')
        condition = self.__getAtomList(script[start_conditions:finish_conditions])
        body, i = self.__getBody(script, finish_conditions)
        return BaseClass.If(condition, body), i

    def __parserElse(self, script):
        start_else = len('else')
        body, i = self.__getBody(script, start_else)
        return BaseClass.Else(body), i

    def __parserFor(self, script):
        start_common_cond = re.search(r'(\()', script).start() + 1
        end_common_cond = start_common_cond + self.__searchForBoundaries(script[start_common_cond:], '[(]', '[)]')

        finish_init = start_common_cond + re.search(r';', script[start_common_cond:end_common_cond]).start() + 1
        init = self.__getAtomList(script[start_common_cond:finish_init])

        finish_cond = finish_init + re.search(r';', script[finish_init:end_common_cond]).start() + 1
        conditions = self.__getAtomList(script[finish_init:finish_cond])

        finish_step = end_common_cond
        step = self.__getAtomList(script[finish_cond:finish_step])

        body, i = self.__getBody(script, end_common_cond)
        return BaseClass.For(init, conditions, step, body), i

    def __parserSwitch(self, script):
        start_conditions = re.search(r'(\()', script).start() + 1
        finish_conditions = start_conditions + self.__searchForBoundaries(script[start_conditions:], '[(]', '[)]')
        condition = self.__getAtomList(script[start_conditions:finish_conditions])

        body = []
        start_body = re.search(r'(\{)', script[finish_conditions:]).start() + finish_conditions
        finish_body = start_body + self.__searchForBoundaries(script[start_body + 1:], '[{]', '[}]') + 1

        i = start_body
        while i < finish_body:
            instr, shift = self.__getSwitchCommand(script[i:finish_body])
            if instr is not None:
                i += shift - 1
                body.append(instr)
            i += 1

        return BaseClass.Switch(condition, body), i

    def __parserDoWhile(self, script):
        start_do = len('do')
        body, i = self.__getBody(script, start_do)

        start_conditions = i + re.search(r'(\()', script[i:]).start() + 1
        finish_conditions = start_conditions + self.__searchForBoundaries(script[start_conditions:], '[(]', '[)]')
        condition = self.__getAtomList(script[start_conditions:finish_conditions])

        return BaseClass.DoWhile(condition, body), finish_conditions

    def __parserOtherInstruction(self, script):
        finish_instruction = self.__searchEndOfCommand(script)
        atoms = self.__getAtomList(script[:finish_instruction])
        return BaseClass.OtherInstruction(atoms), finish_instruction

    @staticmethod
    def __getNumber(script):
        if re.search(r'[^\w]', script) is not None:
            return_len = len(script) - 1
            str_value = script[:-1]
        else:
            str_value = script
            return_len = len(script)

        if '.' in str_value:
            value = float(str_value)
        elif script.startswith('0x') or script.startswith('0X'):
            value = int(str_value, base=16)
        elif script.startswith('0o') or script.startswith('0O'):
            value = int(str_value, base=8)
        elif script.startswith('0b') or script.startswith('0B'):
            value = int(str_value, base=2)
        else:
            value = int(str_value)
        return BaseClass.Number(value), return_len

    @staticmethod
    def __getString(script):
        return BaseClass.String(script), len(script)

    @staticmethod
    def __getVar(script):
        if re.search(r'[^\w\$]', script) is not None:
            name = script[:-1]
        else:
            name = script

        if re.search(r'\.', script) is not None:
            return BaseClass.Var(name), len(name)

        repo = Repository.Repository()
        if (var := repo.search_var(name)) is not None:
            return var, len(name)
        else:
            new_var = BaseClass.Var(name, Parser.__namespace)
            if Parser.__namespace is not None:
                repo.append_var([new_var])
            return new_var, len(name)

    @staticmethod
    def __getBool(script):
        if re.search(r'[^\w]', script) is not None:
            return_len = len(script) - 1
        else:
            return_len = len(script)

        if re.match(r'true', script) is not None:
            return BaseClass.Bool(BaseClass.TypeBool.TRUE), return_len
        else:
            return BaseClass.Bool(BaseClass.TypeBool.FALSE), return_len

    @staticmethod
    def __getArOperation(script):
        if re.match(r'\+=', script) is not None:
            operation_type = BaseClass.TypeArithmeticOperation.ADD_ASSIGN
        elif re.match(r'-=', script) is not None:
            operation_type = BaseClass.TypeArithmeticOperation.SUB_ASSIGN
        elif re.match(r'\*=', script) is not None:
            operation_type = BaseClass.TypeArithmeticOperation.MUl_ASSIGN
        elif re.match(r'/=', script) is not None:
            operation_type = BaseClass.TypeArithmeticOperation.DIV_ASSIGN
        elif re.match(r'\*\*=', script) is not None:
            operation_type = BaseClass.TypeArithmeticOperation.DEG_ASSIGN
        elif re.match(r'%=', script) is not None:
            operation_type = BaseClass.TypeArithmeticOperation.MOD_ASSIGN
        elif re.match(r'\+\+', script) is not None:
            operation_type = BaseClass.TypeArithmeticOperation.INC
        elif re.match(r'\*\*', script) is not None:
            operation_type = BaseClass.TypeArithmeticOperation.DEG
        elif re.match(r'--', script) is not None:
            operation_type = BaseClass.TypeArithmeticOperation.DEC
        elif re.match(r'\+', script) is not None:
            operation_type = BaseClass.TypeArithmeticOperation.ADD
        elif re.match(r'-', script) is not None:
            operation_type = BaseClass.TypeArithmeticOperation.SUB
        elif re.match(r'\*', script) is not None:
            operation_type = BaseClass.TypeArithmeticOperation.MUL
        elif re.match(r'/', script) is not None:
            operation_type = BaseClass.TypeArithmeticOperation.DIV
        elif re.match(r'%', script) is not None:
            operation_type = BaseClass.TypeArithmeticOperation.MOD
        elif re.match(r'=', script) is not None:
            operation_type = BaseClass.TypeArithmeticOperation.ASSIGN

        return BaseClass.ArithmeticOperation(operation_type), len(script)

    @staticmethod
    def __getBinOperation(script):
        if re.match(r'>>>=', script) is not None:
            operation_type = BaseClass.TypeBinaryOperation.RIGHT_SHIFT_FILL_ASSIGN
        elif re.match(r'>>>', script) is not None:
            operation_type = BaseClass.TypeBinaryOperation.RIGHT_SHIFT_FILL
        elif re.match(r'>>=', script) is not None:
            operation_type = BaseClass.TypeBinaryOperation.RIGHT_SHIFT_ASSIGN
        elif re.match(r'>>', script) is not None:
            operation_type = BaseClass.TypeBinaryOperation.RIGHT_SHIFT
        elif re.match(r'<<=', script) is not None:
            operation_type = BaseClass.TypeBinaryOperation.LEFT_SHIFT_ASSIGN
        elif re.match(r'<<', script) is not None:
            operation_type = BaseClass.TypeBinaryOperation.LEFT_SHIF
        elif re.match(r'~=', script) is not None:
            operation_type = BaseClass.TypeBinaryOperation.NOT_ASSIGN
        elif re.match(r'&=', script) is not None:
            operation_type = BaseClass.TypeBinaryOperation.AND_ASSIGN
        elif re.match(r'\|=', script) is not None:
            operation_type = BaseClass.TypeBinaryOperation.OR_ASSIGN
        elif re.match(r'\^=', script) is not None:
            operation_type = BaseClass.TypeBinaryOperation.XOR_ASSIGN
        elif re.match(r'~', script) is not None:
            operation_type = BaseClass.TypeBinaryOperation.NOT
        elif re.match(r'&', script) is not None:
            operation_type = BaseClass.TypeBinaryOperation.AND
        elif re.match(r'\|', script) is not None:
            operation_type = BaseClass.TypeBinaryOperation.OR
        elif re.match(r'\^', script) is not None:
            operation_type = BaseClass.TypeBinaryOperation.XOR

        return BaseClass.BinaryOperation(operation_type), len(script)

    @staticmethod
    def __getLogicalOperation(script):
        if re.match(r'===', script) is not None:
            operation_type = BaseClass.TypeLogicalOperation.TRIPLE_EQ
        elif re.match(r'!==', script) is not None:
            operation_type = BaseClass.TypeLogicalOperation.TRIPLE_NE
        elif re.match(r'==', script) is not None:
            operation_type = BaseClass.TypeLogicalOperation.EQ
        elif re.match(r'!=', script) is not None:
            operation_type = BaseClass.TypeLogicalOperation.NE
        elif re.match(r'<=', script) is not None:
            operation_type = BaseClass.TypeLogicalOperation.LESS_EQ
        elif re.match(r'>=', script) is not None:
            operation_type = BaseClass.TypeLogicalOperation.GREATER_EQ
        elif re.match(r'\?\?=', script) is not None:
            operation_type = BaseClass.TypeLogicalOperation.NULLISH_ASSIGN
        elif re.match(r'&&=', script) is not None:
            operation_type = BaseClass.TypeLogicalOperation.AND_ASSIGN
        elif re.match(r'\|\|=', script) is not None:
            operation_type = BaseClass.TypeLogicalOperation.OR_ASSIGN
        elif re.match(r'&&', script) is not None:
            operation_type = BaseClass.TypeLogicalOperation.AND
        elif re.match(r'\|\|', script) is not None:
            operation_type = BaseClass.TypeLogicalOperation.OR
        elif re.match(r'!', script) is not None:
            operation_type = BaseClass.TypeLogicalOperation.NOT
        elif re.match(r'\?\?', script) is not None:
            operation_type = BaseClass.TypeLogicalOperation.NULLISH
        elif re.match(r'<', script) is not None:
            operation_type = BaseClass.TypeLogicalOperation.LESS
        elif re.match(r'>', script) is not None:
            operation_type = BaseClass.TypeLogicalOperation.GREATER
        elif re.match(r'\?', script) is not None:
            operation_type = BaseClass.TypeLogicalOperation.SHORT_IF
        elif re.match(r':', script) is not None:
            operation_type = BaseClass.TypeLogicalOperation.SHORT_COND

        return BaseClass.LogicalOperation(operation_type), len(script)

    @staticmethod
    def __getBorder():
        return BaseClass.Border(), 1

    @staticmethod
    def __getNew():
        return BaseClass.New(), len('new ')

    @staticmethod
    def __getConst():
        return BaseClass.Const(), len('const ')

    @staticmethod
    def __getInfinity():
        return BaseClass.Infinity(), len('Infinity')

    def __getArray(self, script):
        start_array = re.search(r'(\[)', script).start() + 1
        finish_array = start_array + self.__searchForBoundaries(script[start_array:], r'\[', r'\]')
        atoms = self.__getAtomList(script[start_array:finish_array - 1])
        return BaseClass.Array(atoms), finish_array - 1

    def __getBrackets(self, script):
        start_brackets = re.search(r'(\()', script).start() + 1
        finish_brackets = start_brackets + self.__searchForBoundaries(script[start_brackets:], '[(]', '[)]')

        atoms = self.__getAtomList(script[start_brackets:finish_brackets - 1])
        return BaseClass.Brackets(atoms), finish_brackets

    def __getCallFunc(self, script):
        start_args = re.search(r'(\()', script).start() + 1
        finish_args = start_args + self.__searchForBoundaries(script[start_args:], '[(]', '[)]')

        name = script[:start_args - 1]
        args = self.__getAtomList(script[start_args:finish_args - 1])

        repo = Repository.Repository()
        if (func := repo.search_func(name)) is not None:
            call_func = BaseClass.CallFunc(func, args)
        else:
            func = BaseClass.Func(name)
            repo.append_func(func)
            call_func = BaseClass.CallFunc(func, args)

        if len(script) > finish_args and script[finish_args] == '.':
            old_namespace = Parser.__namespace
            Parser.__namespace = None
            atom, shift = self.__getAtom(script[finish_args + 1:])
            Parser.__namespace = old_namespace
            return BaseClass.InstanceClass(call_func, atom), finish_args + shift + 1

        return call_func, finish_args

    def __getSwitchCommand(self, script):
        if re.match(r'case[\W]', script) is not None:
            command_type = BaseClass.TypeSwitchCommand.CASE
        elif re.match(r'default[\W]', script) is not None:
            command_type = BaseClass.TypeSwitchCommand.DEFAULT
        else:
            return None, 0

        start_body = re.search(r':', script).start() + 1
        condition = self.__getAtomList(script[len('case') if command_type == BaseClass.TypeSwitchCommand.CASE
                                              else len('default'):start_body - 1])

        i, body = start_body, []
        while i < len(script):
            if re.match(r'case[\W]', script[i:]) is not None or\
                    re.match(r'default[\W]', script[i:]) is not None:
                i -= 1
                break
            instr, shift = self.__getInstruction(script[i:])
            if instr is not None:
                i += shift - 1
                body.append(instr)
            i += 1

        return BaseClass.SwitchCommand(command_type, condition, body), i

    def __getInstanceClass(self, script):
        old_namespace = Parser.__namespace
        Parser.__namespace = None
        start = re.search(r'\.', script).start()
        instance, shift = self.__getAtom(script[:start])
        atom, shift = self.__getAtom(script[start + 1:])
        Parser.__namespace = old_namespace
        return BaseClass.InstanceClass(instance, atom), start + shift + 1

    def __getAtom(self, script):
        if (match := re.match(r'(((0o[0-7]+)|(0x[\dabcdef]+)|(0b[0-1]+)|(\d+(\.\d+)*))([^\w]|$))', script,
                              re.IGNORECASE)) is not None:
            return self.__getNumber(match.group())
        elif (match := re.match(r'(\'(\\\'|.)*?\'|\"(\\\"|.)*?\")', script)) is not None:
            return self.__getString(match.group())
        elif re.match(r'\[', script) is not None:
            return self.__getArray(script)
        elif re.match(r'\(', script) is not None:
            return self.__getBrackets(script)
        elif re.match(r'function[\W]', script) is not None:
            return self.__parserFunc(script)
        elif re.match(r'([\w\$]+\.)', script) is not None:
            return self.__getInstanceClass(script)
        elif re.match(r'([\w\$]+\s*\()', script) is not None:
            return self.__getCallFunc(script)
        elif re.match(r'((true)|(false)([^\w]|$))', script) is not None:
            return self.__getBool(script)
        elif re.match(r'((new)([^\w\$]|$))', script) is not None:
            return self.__getNew()
        elif re.match(r'((const)([^\w\$]|$))', script) is not None:
            return self.__getConst()
        elif re.match(r'((Infinity)([^\w\$]|$))', script) is not None:
            return self.__getInfinity()
        elif (match := re.match(r'([\w\$]+([^\w\$]|$))', script)) is not None:
            return self.__getVar(match.group())
        elif (match := re.match(r'((\+=)|(-=)|(\*=)|(/=)|(\*\*=)|(%=))', script)) is not None:
            return self.__getArOperation(match.group())
        elif (match := re.match(r'((\+\+)|(--)|(\*\*))', script)) is not None:
            return self.__getArOperation(match.group())
        elif (match := re.match(r'((>>>=)|(>>>)|(>>=)|(>>)|(<<=)|(<<))', script)) is not None:
            return self.__getBinOperation(match.group())
        elif (match := re.match(r'((~=)|(&=)|(\|=)|(\^=))', script)) is not None:
            return self.__getBinOperation(match.group())
        elif (match := re.match(r'((===)|(!==)|(==)|(!=)|(<=)|(>=)|(&&=)|(\|\|=)|(\?\?=))', script)) is not None:
            return self.__getLogicalOperation(match.group())
        elif (match := re.match(r'((!)|(<)|(>)|(&&)|(\|\|)|(\?\?))', script)) is not None:
            return self.__getLogicalOperation(match.group())
        elif (match := re.match(r'((~)|(&)|(\|)|(\^))', script)) is not None:
            return self.__getBinOperation(match.group())
        elif (match := re.match(r'((\+)|(-)|(\*)|(/)|(%)|(=))', script)) is not None:
            return self.__getArOperation(match.group())
        elif (match := re.match(r'((\?)|(:))', script)) is not None:
            return self.__getLogicalOperation(match.group())
        elif re.match(r',', script) is not None:
            return self.__getBorder()

        return None, 0

    def __getInstruction(self, script):
        if re.match(r'function[\W]', script) is not None:
            return self.__parserFunc(script)
        elif re.match(r'var ', script) is not None:
            return self.__parserDeclaration(script)
        elif re.match(r'let ', script) is not None:
            return self.__parserDeclaration(script)
        elif re.match(r'break[\W]', script) is not None:
            return self.__parserCycleControl(script)
        elif re.match(r'continue[\W]', script) is not None:
            return self.__parserCycleControl(script)
        elif re.match(r'return[\W]', script) is not None:
            return self.__parserReturn(script)
        elif re.match(r'while[\W]', script) is not None:
            return self.__parserWhile(script)
        elif re.match(r'if[\W]', script) is not None:
            return self.__parserIf(script)
        elif re.match(r'else[\W]', script) is not None:
            return self.__parserElse(script)
        elif re.match(r'for[\W]', script) is not None:
            return self.__parserFor(script)
        elif re.match(r'switch[\W]', script) is not None:
            return self.__parserSwitch(script)
        elif re.match(r'do[\W]', script) is not None:
            return self.__parserDoWhile(script)
        elif re.match(r'[\w\$\!]', script) is not None:
            return self.__parserOtherInstruction(script)
        return None, 0

    def __getBody(self, script, start_position):
        body = []
        # checking count of instruction (one or { })
        if re.match(r'\s*{', script[start_position:]) is not None:
            start_body = re.search(r'(\{)', script[start_position:]).start() + start_position
            finish_body = start_body + self.__searchForBoundaries(script[start_body + 1:], '[{]', '[}]') + 1

            i = start_body
            while i < finish_body:
                instr, shift = self.__getInstruction(script[i:])
                if instr is not None:
                    i += shift - 1
                    body.append(instr)
                i += 1
        else:
            i, count_instruction = start_position, 0
            while not count_instruction:
                instr, shift = self.__getInstruction(script[i:])
                if instr is not None:
                    i += shift - 1
                    body.append(instr)
                    count_instruction += 1
                i += 1

        return body, i

    def __getAtomList(self, script):
        i = 0
        atoms = []
        while i < len(script):
            atom, shift = self.__getAtom(script[i:])
            if atom is not None:
                i += shift - 1
                atoms.append(atom)
            i += 1

        return atoms

    @staticmethod
    def __searchForBoundaries(script, start_bound, finish_bound):
        cnt_bracket, shift = 1, 0
        while shift < len(script) and cnt_bracket:
            if (match := re.match(r'(\'(\\\'|.)*?\'|\"(\\\"|.)*?\")|(' + start_bound + ')|(' + finish_bound + ')',
                                  script[shift:])) is not None:
                if match.group() == start_bound[1]:
                    cnt_bracket += 1
                elif match.group() == finish_bound[1]:
                    cnt_bracket -= 1
                else:
                    shift += match.end() - 1
            shift += 1
        return shift

    @staticmethod
    def __searchEndOfCommand(script):
        shift = 0
        while shift < len(script):
            if (match := re.match(r'(\{((\'(\\\'|.)*?\'|\"(\\\"|.)*?\")|.)+?\})|(\'(\\\'|.)*?\'|\"(\\\"|.)*?\")|(;)', script[shift:])) is not None:
                if match.group() == ';':
                    return shift
                else:
                    shift += match.end() - 1
            shift += 1
        raise ValueError('[search_end_of_command]: symbol \';\' was not found')
