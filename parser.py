from __future__ import annotations
from lexer import Lexer, Token

id_tokens = (Token.ID, Token.STRING_LITERAL_2, Token.STRING_LITERAL_1, Token.FLOAT_LITERAL,
             Token.INT_LITERAL,)

class Node:
    _fields = ()

    def __get_class_name(self):
        c = str(self.__class__)
        pos_1 = c.find('.') + 1
        pos_2 = c.find("'", pos_1)
        return f"{c[pos_1:pos_2]}"

    def __repr__(self, level=0, parent_field_name=''):
        if level == 0:
            res = ''
        else:
            res = '|   ' * level
            res += "|+-"
        res += f"{parent_field_name}: {self.__get_class_name()}\n"
        for field_name, el in iter_child_nodes(self):
            if isinstance(el, Token):
                res += '|   ' * (level + 1)
                res += "|+-"
                res += f'{field_name}: {el}\n'
            else:
                res += el.__repr__(level + 1, field_name)
        return res


class NodeProgram(Node):
    def __init__(self, block):
        self.block = block

    _fields = ('block',)


class NodeBlock(Node):
    def __init__(self, children):
        self.children = children

    _fields = ('children',)


class NodeElseBlock(Node):
    def __init__(self, block):
        self.block = block

    _fields = ('block', )


class NodeDeclaration(Node):
    def __init__(self, _type, _name, const=None):
        self.type = _type
        self.name = _name
        self.const = const

    _fields = ('type', 'name', 'const',)


class NodeAssigning(Node):
    def __init__(self, left_side, right_side):
        self.left_side = left_side
        self.right_side = right_side

    _fields = ('left_side', 'right_side')


class NodeFunction(Node):
    def __init__(self, ret_type: Token, name: Token, formal_params: NodeFormalParams, block):
        self.ret_type = ret_type
        self.name = name
        self.formal_params = formal_params
        self.block = block

    _fields = ('ret_type', 'name', 'formal_params', 'block')


class NodeSequence(Node):
    def __init__(self, members):
        self.members = members

    _fields = ('members',)


class NodeParams(Node):
    def __init__(self, params):
        self.params = params

    _fields = ('params',)


# class NodeMultipleDeclarations(NodeParams):
#    pass


class NodeFormalParams(NodeParams):
    pass


class NodeMultipleDeclarations(Node):
    #def __init__(self, typev, names):
    def __init__(self, names):
        #self.type = typev
        self.names = names

    #_fields = ('type', 'names')
    _fields = ('names',)


class NodeActualParams(NodeParams):
    pass


class NodeIfConstruction(Node):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block
        # self.else_block = else_block

    _fields = ('condition', 'block')


class NodeWhileConstruction(Node):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block

    _fields = ('condition', 'block')


class NodeReturnStatement(Node):
    def __init__(self, expression):
        self.expression = expression

    _fields = ('expression',)


class NodeLiteral(Node):
    def __init__(self, value):
        self.value = value

    _fields = ('value',)


class NodeStringLiteral(NodeLiteral):
    pass


class NodeIntLiteral(NodeLiteral):
    pass


class NodeFloatLiteral(NodeLiteral):
    pass


class NodeVar(Node):
    def __init__(self, name):
        self.name = name

    _fields = ('name',)


class NodeAtomType(Node):
    def __init__(self, _id):
        self.id = _id

    _fields = ('id',)


class NodeAtomTypeSequence(Node):
    def __init__(self, _id):
        self.id = _id

    _fields = ('id',)


class NodeComplexType(Node):
    def __init__(self, name, size):
        self.name = name
        self.size = size

    _fields = ('name', 'size')


class NodeFunctionCall(Node):
    def __init__(self, name, actual_params):
        self.name = name
        self.actual_params = actual_params

    _fields = ('name', 'actual_params')


class NodeIndexAccess(Node):
    def __init__(self, var, index):
        self.var = var
        self.index = index

    _fields = ('var', 'index')

class NodeUnaryOperator(Node):
    def __init__(self, operand):
        self.operand = operand

    _fields = ('operand',)


class NodeUnaryMinus(NodeUnaryOperator):
    pass


class NodeNot(NodeUnaryOperator):
    pass


class NodeID(Node):
    def __init__(self, name):
        self.name = name

    _fields = ('name',)


class NodeCin(Node):
    def __init__(self, variables):
        self.variables = variables

    _fields = ('variables',)

class NodeCout(Node):
    def __init__(self, variables):
        self.variables = variables

    _fields = ('variables',)

class NodeBinaryOperator(Node):
    def __init__(self, left:Token, op:Token, right:Token):
        self.op = op
        self.left = left
        self.right = right

    _fields = ('left', 'op', 'right')


# class NodeL(NodeBinaryOperator):
#     pass
#
#
# class NodeG(NodeBinaryOperator):
#     pass
#
#
# class NodeLE(NodeBinaryOperator):
#     pass
#
#
# class NodeGE(NodeBinaryOperator):
#     pass
#
#
# class NodeEQ(NodeBinaryOperator):
#     pass
#
#
# class NodeNEQ(NodeBinaryOperator):
#     pass
#
#
# class NodeOr(NodeBinaryOperator):
#     pass
#
#
# class NodeAnd(NodeBinaryOperator):
#     pass
#
#
# class NodePlus(NodeBinaryOperator):
#     pass
#
#
# class NodeMinus(NodeBinaryOperator):
#     pass
#
#
# class NodeDivision(NodeBinaryOperator):
#     pass
#
#
# class NodeMultiply(NodeBinaryOperator):
#     pass
#
#
# class NodeIDivision(NodeBinaryOperator):
#     pass

#
# class NodeMod(NodeBinaryOperator):
#     pass


class NodeComment(Node):
    def __init__(self, _text):
        self.comment = _text

    _fields = ('comment', )


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.token = None
        #self.token = self.lexer.get_next_token()

    def next_token(self):
        self.token = self.lexer.get_next_token()

    def require(self, *expected_token_name):
        while self.token.name == Token.NEWLINE:
            self.next_token()
        if self.token.name not in expected_token_name:
            self.error(f"Ожидается токен {', '.join([Token.token_names[exp_token] for exp_token in expected_token_name])}!")

    def error(self, msg):
        # print(f'Ошибка синтаксического анализа ({self.lexer.lineno}, {self.lexer.pos}): {msg}')
        # sys.exit(1)
        raise RuntimeError(
            f'Ошибка синтаксического анализа ({self.lexer.lineno}, {self.lexer.pos}, {self.token}): {msg}')

    def block(self) -> Node:
        statements = []
        while self.token.name not in {Token.RCBR, Token.EOF}:
            statement_to_add = self.statement()
            if not statement_to_add:
                continue
            statements.append(statement_to_add)
            # statements.append(self.statement())
            # self.require(Token.SEMI)
            match statement_to_add:
                case NodeComment():
                    pass
                    # print('Комментариям не нужна ";"')
                case NodeFunction() | NodeWhileConstruction() | NodeIfConstruction() | NodeElseBlock():
                    pass
                    # print('Блокам не нужна ";"')
                case _:
                    self.require(Token.SEMI)
            self.next_token()
        return NodeBlock(statements)

    def else_block(self) -> Node:
        statements = []
        while self.token.name not in {Token.RCBR, Token.EOF}:
            statement_to_add = self.statement()
            if not statement_to_add:
                continue
            statements.append()
            self.require(Token.SEMI)
            self.next_token()
        return NodeElseBlock(statements)

    def actual_params(self) -> Node:
        params = []
        while self.token.name not in {Token.RBR, Token.EOF}:
            params.append(self.expression())
            if self.token.name == Token.COMMA:
                self.next_token()
        return NodeActualParams(params)

    def formal_params(self) -> Node:
        params = []
        while self.token.name not in {Token.RBR, Token.EOF}:
            params.append(self.declaration())

            if self.token.name == Token.COMMA:
                self.next_token()
        return NodeFormalParams(params)

    # Объявление через запятую
    def multiple_declarations(self, first_token, first_name, const=None) -> Node:
        # params = [first_name]
        params = [NodeDeclaration(first_token, first_name, const)]
        while self.token.name not in {Token.SEMI, Token.EOF}:
            if self.token.name == Token.COMMA:
                self.next_token()
                first_name = self.token
                params.append(self.declaration(first_token, const))

            if self.token.name == Token.ASSIGN:
                self.next_token()
                #params.append(NodeAssigning(first_name, self.token))
                params.append(NodeAssigning(NodeVar(first_name), self.expression()))
                #self.next_token()
            # params.append(self.multiple_declarations(first_token, ))
        #return NodeMultipleDeclarations(first_token, params)
        return NodeMultipleDeclarations(params)

    def operand(self) -> Node:
        first_token = self.token
        match self.token.name:
            case Token.STRING_LITERAL_1:
                self.next_token()
                return NodeStringLiteral(first_token)
            case Token.STRING_LITERAL_2:
                self.next_token()
                return NodeStringLiteral(first_token)
            case Token.INT_LITERAL:
                self.next_token()
                return NodeIntLiteral(first_token)
            case Token.FLOAT_LITERAL:
                self.next_token()
                return NodeFloatLiteral(first_token)
            case Token.ID:
                self.next_token()
                match self.token.name:
                    case Token.LBR:
                        self.next_token()
                        actual_params = self.actual_params()
                        self.require(Token.RBR)
                        self.next_token()
                        return NodeFunctionCall(first_token, actual_params)
                    case Token.LSBR:
                        self.next_token()
                        index = self.expression()
                        self.require(Token.RSBR)
                        self.next_token()
                        return NodeIndexAccess(NodeVar(first_token), index)
                    case _:
                        return NodeVar(first_token)
            case Token.LBR:
                self.next_token()
                expression = self.expression()
                self.require(Token.RBR)
                self.next_token()
                return expression

    def factor(self) -> Node:
        match self.token.name:
            case Token.MINUS:
                self.next_token()
                return NodeUnaryMinus(self.operand())
            case _:
                return self.operand()

    def term(self) -> Node:
        left = self.factor()
        op = self.token
        op_name = self.token.name
        while op_name in {Token.ASTERISK, Token.SLASH, Token.PERCENT}:
            self.next_token()
            left = NodeBinaryOperator(left, op, self.factor())
            op_name = self.token.name
        return left

    def expression(self) -> Node:
        left = self.term()
        op = self.token
        op_name = self.token.name
        while op_name in {Token.PLUS, Token.MINUS}:
            self.next_token()
            left = NodeBinaryOperator(left, op, self.term())
            op_name = self.token.name
        return left

    def logical_operand(self) -> Node:
        match self.token.name:
            case Token.NOT:
                self.next_token()
                return NodeNot(self.logical_operand())
            case Token.LBR:
                self.next_token()
                condition = self.condition()
                self.require(Token.RBR)
                self.next_token()
                return condition
            case _:
                return self.expression()

    def and_operand(self) -> Node:
        left = self.logical_operand()
        op_name = self.token.name
        op = self.token
        while op_name in {Token.L, Token.G, Token.LE, Token.GE, Token.EQ, Token.NEQ}:
            self.next_token()
            left = NodeBinaryOperator(left, op, self.expression())
            op_name = self.token.name
        return left

    def or_operand(self) -> Node:
        left = self.and_operand()
        op = self.token
        op_name = self.token.name
        while op_name == Token.AND:
            self.next_token()
            # left = NodeAnd(left, self.and_operand())
            left = NodeBinaryOperator(left,op, self.and_operand())
            op_name = self.token.name
        return left

    def condition(self) -> Node:
        left = self.or_operand()
        op = self.token
        op_name = self.token.name
        while op_name == Token.OR:
            self.next_token()
            # left = NodeOr(left, self.or_operand())
            left = NodeBinaryOperator(left, op, self.or_operand())
            op_name = self.token.name
        return left

    def type(self) -> Node:
        _id = self.token
        self.next_token()
        if self.token.name != Token.LSBR:
            return _id
        self.next_token()
        self.require(Token.INT_LITERAL)
        size = self.token
        self.next_token()
        self.require(Token.RSBR)
        self.next_token()
        return NodeComplexType(id, size)

    # В С++ последовательность массива начинается с { и заканчивается }
    def sequence(self) -> Node:
        members = []
        while self.token.name not in {Token.RSBR, Token.EOF}:
            members.append(self.expression())
            if self.token.name == Token.COMMA:
                self.next_token()
        return NodeSequence(members)

    def declaration(self, passed_type=None, const=False) -> Node:
        if not passed_type:
            self.require(Token.ID)
            _type = self.type()
        else:
            _type = passed_type
        self.require(Token.ID)
        _id = self.token
        self.next_token()
        return NodeDeclaration(_type, _id, const)

    def cin_cout(self) -> Node:
        #self.require(Token.ID, Token.STRING_LITERAL_1, Token.STRING_LITERAL_2)
        self.require(*id_tokens)
        _id = self.token
        self.next_token()
        match _id.name:

            case Token.STRING_LITERAL_1 | Token.STRING_LITERAL_2:
                return NodeStringLiteral(_id)
            case Token.INT_LITERAL:
                return NodeIntLiteral(_id)
            case Token.FLOAT_LITERAL:
                return NodeFloatLiteral
            case _: # Token.ID:
                return NodeID(_id)
    def statement(self) -> Node:
        match self.token.name:
            # declaration | assigning | function-call

            case Token.ID | Token.CONST:
                _const = self.token.name == Token.CONST
                if _const:
                    const_token = self.token
                    self.next_token()
                else:
                    const_token = None

                first_token = self.token
                self.next_token()
                match self.token.name:
                    # например int abc
                    case Token.ID:
                        name = self.token
                        self.next_token()
                        # объявление функции
                        if self.token.name == Token.LBR:
                            self.next_token()
                            # начинаем разбор формальных параметров
                            formal_params = self.formal_params()
                            # после разбора формальных параметров лексер должен смотреть на закрывающую скобку )
                            self.require(Token.RBR)
                            # пропускаем скобку
                            self.next_token()
                            # следующий токен { - скобка перед телом функции
                            self.require(Token.LCBR)
                            # пропускаем скобку
                            self.next_token()
                            # начинаем разбирать тело
                            block = self.block()
                            # после разбора тела функции мы должны встретить закрывающую скобку }
                            self.require(Token.RCBR)
                            self.next_token()
                            return NodeFunction(first_token, name, formal_params, block)
                        elif self.token.name in {Token.COMMA, Token.ASSIGN}:
                            return self.multiple_declarations(first_token, name, const=const_token)
                        elif self.token.name == Token.ASSIGN:
                            if self.token.name == Token.ASSIGN:
                                pass
                        else:
                            #return NodeDeclaration(NodeAtomType(first_token), name, const_token)
                            return NodeDeclaration(first_token, name, const_token)
                    # например int[10] abc -> int abc[10]
                    case Token.LSBR:
                        self.next_token()
                        self.require(Token.INT_LITERAL)
                        size = self.token
                        self.next_token()
                        self.require(Token.RSBR)
                        self.next_token()
                        self.require(Token.ID)
                        name = self.token
                        self.next_token()
                        return NodeDeclaration(NodeComplexType(first_token, size), name)
                    # например abc = 123 или abc = [1,2,3]
                    case Token.ASSIGN:
                        self.next_token()
                        if self.token.name != Token.LSBR:
                            return NodeAssigning(NodeVar(first_token), self.expression())
                        self.next_token()
                        sequence = self.sequence()
                        self.require(Token.RSBR)
                        self.next_token()
                        return NodeAssigning(NodeVar(first_token), sequence)
                    # например abc(1,3,4)
                    case Token.LBR:
                        self.next_token()
                        actual_params = self.actual_params()
                        self.require(Token.RBR)
                        self.next_token()
                        return NodeFunctionCall(first_token, actual_params)
                    case _:
                        self.error("Ожидалось объявление переменной, присваивание или вызов функции!")

            case Token.WHILE:
                block, condition = self.get_while_if_else_body()
                # self.next_token()
                return NodeWhileConstruction(condition, block)
            case Token.IF:
                block, condition = self.get_while_if_else_body()
                # self.next_token()
                return NodeIfConstruction(condition, block)
            case Token.ELSE:
                block, condition = self.get_while_if_else_body()
                # self.next_token()
                return NodeElseBlock(block)

            case Token.RETURN:
                self.next_token()
                expression = self.expression()
                return NodeReturnStatement(expression)

            case Token.CIN:
                self.next_token()
                self.require(Token.DG)
                self.next_token()
                variables = []
                while self.token.name not in {Token.SEMI, Token.EOF}:
                    variables.append(self.cin_cout())
                    if self.token.name == Token.DG:
                        self.next_token()
                return NodeCin(variables)

            case Token.COUT:
                self.next_token()
                self.require(Token.DL)
                self.next_token()
                variables = []
                while self.token.name not in {Token.SEMI, Token.EOF}:
                    variables.append(self.cin_cout())
                    if self.token.name == Token.DL:
                        self.next_token()
                return NodeCout(variables)

            # аналогично определению
            #case Token.CONST:
            case Token.ELSE:
                self.next_token()
                first_token = self.token
                self.next_token()
                match self.token.name:
                    # например const int abc
                    case Token.ID:
                        name = self.token
                        self.next_token()
                        #return NodeDeclaration(NodeAtomType(first_token), name)
                        return NodeDeclaration(first_token, name)
                    # например int[10] abc
                    case Token.LSBR:
                        self.next_token()
                        self.require(Token.INT_LITERAL)
                        size = self.token
                        self.next_token()
                        self.require(Token.RSBR)
                        self.next_token()
                        self.require(Token.ID)
                        name = self.token
                        self.next_token()
                        return NodeDeclaration(NodeComplexType(first_token, size), name)
                    # например abc = 123 или abc = [1,2,3]
                    case Token.ASSIGN:
                        self.next_token()
                        if self.token.name != Token.LSBR:
                            return NodeAssigning(NodeVar(first_token), self.expression())
                        self.next_token()
                        sequence = self.sequence()
                        self.require(Token.RSBR)
                        self.next_token()
                        return NodeAssigning(NodeVar(first_token), sequence)
                    # например abc(1,3,4)
                    case Token.LBR:
                        self.next_token()
                        actual_params = self.actual_params()
                        self.require(Token.RBR)
                        self.next_token()
                        return NodeFunctionCall(first_token, actual_params)
                    case _:
                        self.error("Ожидалось объявление константы и присваивание!")
            case Token.DSLASH:
                comment = self.token
                self.next_token()
                while self.token.name != Token.NEWLINE:
                    self.next_token()
                return NodeComment(comment)
            case Token.NEWLINE:
                self.next_token()
                return None


    def get_while_if_else_body(self):
        self.next_token()
        if self.token.name != Token.ELSE:
            condition = self.condition()
        else:
            condition = None
        self.require(Token.LCBR)
        self.next_token()
        block = self.block()
        self.require(Token.RCBR)
        return block, condition

    def parse(self) -> Node:
        if not self.token:
            self.token = self.lexer.get_next_token()
        if self.token.name == Token.EOF:
            self.error("Пустой файл!")
        else:
            statements = []
            while self.token.name != Token.EOF:
                statement_to_add = self.statement()
                if not statement_to_add:
                    continue
                statements.append(statement_to_add)
                # функции не нужна ;

                match statement_to_add:
                    case NodeComment():
                        pass
                        # print('Комментариям не нужна ";"')
                    case NodeFunction() | NodeWhileConstruction() | NodeIfConstruction() | NodeElseBlock():
                        pass
                        # print('Блокам не нужна ";"')
                    case _:
                        self.require(Token.SEMI)

                self.next_token()
            return NodeProgram(statements)


def iter_fields(node):
    for field in node._fields:
        try:
            yield field, getattr(node, field)
        except AttributeError:
            # print(f'no field ')
            pass


def iter_child_nodes(node):
    if isinstance(node, Token):
        return None, node
    for name, field in iter_fields(node):
        if isinstance(field, Token):
            yield name, field
        elif isinstance(field, Node):
            yield name, field
        elif isinstance(field, list):
            for item in field:
                if isinstance(item, Node):
                    yield name, item
