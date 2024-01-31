import sys


class Token:
    EOF, STRING_LITERAL_1, STRING_LITERAL_2, ID, INT_LITERAL, \
        FLOAT_LITERAL, ASSIGN, L, G, EQ, NEQ, \
        PLUS, MINUS, ASTERISK, SLASH, DSLASH, LINK, \
        PERCENT, LBR, RBR, LCBR, RCBR, LSBR, \
        RSBR, LE, GE, SEMI, COMMA, \
        FOR, WHILE, RETURN, FUNCTION, IF, ELSE, COUT, CIN, DL, DG, CONST, \
        COMMENTSTART, COMMENTEND, \
        OR, AND, NOT, NEWLINE = range(45)

    token_names = {
        EOF: "EOF",
        STRING_LITERAL_1: "STR-LTRL_1",
        STRING_LITERAL_2: "STR-LTRL_2",
        ID: "ID",
        INT_LITERAL: "INT-LTRL",
        FLOAT_LITERAL: "FLOAT-LTRL",
        ASSIGN: "ASSIGN '='",
        L: "L '<'",
        G: "G '>'",
        DL: "DL '<<'",
        DG: "DG '>>'",
        EQ: "EQ '=='",
        PLUS: "PLUS '+'",
        MINUS: "MINUS '-'",
        ASTERISK: "ASTERISK '*'",
        SLASH: "SLASH '/'",
        DSLASH: "DSLASH '//'",
        PERCENT: "PERCENT '%'",
        LBR: "LBR '('",
        RBR: "RBR ')'",
        LCBR: "LCBR '{'",
        RCBR: "RCBR '}'",
        LSBR: "LSBR '['",
        RSBR: "RSBR ']'",
        LE: "LE '<='",
        GE: "GE '>='",
        SEMI: "SEMI ';'",
        COMMA: "COMMA ','",
        FOR: "FOR",
        WHILE: "WHILE",
        RETURN: "RETURN",
        FUNCTION: "FUNCTION",
        IF: "IF",
        LINK: "LINK '&'",
        AND: "AND '&&'",
        OR: "OR '||'",
        ELSE: "ELSE",
        COUT: "COUT",
        CIN: "CIN",
        CONST: "CONST",
        COMMENTSTART: "COMMENTSTART '/*'",
        COMMENTEND: "COMMENTEND '*/'",
        NEWLINE: "NEWLINE '\\n'"

    }

    KEYWORDS = {
        'for': FOR,
        'while': WHILE,
        'return': RETURN,
        'function': FUNCTION,
        'if': IF,
        'else': ELSE,
        'not': NOT,
        'cout': COUT,
        'cin': CIN,
        'const': CONST,
    }

    def __init__(self, token, value, lineno, pos):
        self.name = token
        self.value = value
        self.lineno = lineno
        self.pos = pos

    def __repr__(self):
        return f'({self.token_names[self.name]}, {self.value}, ({self.lineno}, {self.pos}))'



class Lexer:
    def __init__(self, content):
        self.content = content
        self.cursor = 0
        self.lineno = 1
        self.pos = 1
        self.state = None
        self.char = None
        self.length = len(content)-1

    def ___init__(self, file):
        self.file = file
        self.lineno = 1
        self.pos = 1
        self.state = None
        self.char = None


    def __get_next_char(self):
        if self.cursor > self.length:
            self.char = '' # EOF
        else:
            self.char = self.content[self.cursor]
            self.cursor += 1
            self.pos += 1
            if self.char == '\n':
                self.lineno += 1
                self.pos = 1

    def error(self, msg):
        #print(f'Ошибка лексического анализа ({self.lineno}, {self.pos}): {msg}')
        #sys.exit(1)
        raise RuntimeError(f'Ошибка лексического анализа ({self.lineno}, {self.pos}): {msg}')

    def get_next_token(self):
        match self.state:
            case None:
                if self.char is None:
                    self.__get_next_char()
                    return self.get_next_token()
                elif self.char == '\n':
                    self.__get_next_char()
                    return Token(Token.NEWLINE, "\\n", self.lineno, self.pos)
                elif self.char in ['\t',' ',]:
                    self.__get_next_char()
                    return self.get_next_token()
                elif self.char == '':
                    return Token(Token.EOF, "", self.lineno, self.pos)
                elif self.char == '+':
                    self.__get_next_char()
                    return Token(Token.PLUS, "+", self.lineno, self.pos)
                elif self.char == '-':
                    self.__get_next_char()
                    return Token(Token.MINUS, "-", self.lineno, self.pos)
                elif self.char == '*':
                    self.__get_next_char()
                    return Token(Token.ASTERISK, "*", self.lineno, self.pos)
                elif self.char == '%':
                    self.__get_next_char()
                    return Token(Token.PERCENT, "%", self.lineno, self.pos)
                elif self.char == '(':
                    self.__get_next_char()
                    return Token(Token.LBR, "(", self.lineno, self.pos)
                elif self.char == ')':
                    self.__get_next_char()
                    return Token(Token.RBR, ")", self.lineno, self.pos)
                elif self.char == '{':
                    self.__get_next_char()
                    return Token(Token.LCBR, "{", self.lineno, self.pos)
                elif self.char == '}':
                    self.__get_next_char()
                    return Token(Token.RCBR, "}", self.lineno, self.pos)
                elif self.char == '[':
                    self.__get_next_char()
                    return Token(Token.LSBR, "[", self.lineno, self.pos)
                elif self.char == ']':
                    self.__get_next_char()
                    return Token(Token.RSBR, "]", self.lineno, self.pos)
                elif self.char == ';':
                    self.__get_next_char()
                    return Token(Token.SEMI, ";", self.lineno, self.pos)
                elif self.char == ',':
                    self.__get_next_char()
                    return Token(Token.COMMA, ",", self.lineno, self.pos)
                elif self.char == '!':
                    self.__get_next_char()
                    if self.char == '=':
                        self.__get_next_char()
                        return Token(Token.NEQ, "!=", self.lineno, self.pos)
                    else:
                        self.error("Ожидался оператор !=")
                elif self.char == '/':
                    self.state = Token.SLASH
                    return self.get_next_token()
                elif self.char == '=':
                    self.state = Token.ASSIGN
                    return self.get_next_token()
                elif self.char == '<':
                    self.state = Token.L
                    return self.get_next_token()
                elif self.char == '>':
                    self.state = Token.G
                    return self.get_next_token()
                elif self.char == '"':
                    self.state = Token.STRING_LITERAL_1
                    return self.get_next_token()
                elif self.char == "'":
                    self.state = Token.STRING_LITERAL_2
                    return self.get_next_token()
                elif self.char.isalpha() or self.char == '_':
                    self.state = Token.ID
                    return self.get_next_token()
                elif self.char.isdigit():
                    self.state = Token.INT_LITERAL
                    return self.get_next_token()
                elif self.char == '&':
                    self.state = Token.AND
                    return self.get_next_token()
                elif self.char == '|':
                    self.state = Token.OR
                    return self.get_next_token()
                else:
                    self.error("Неожиданный символ")
            case Token.SLASH:
                self.__get_next_char()
                if self.char == '/':
                    self.state = Token.DSLASH
                    #self.__get_next_char()
                    #return Token(Token.DSLASH, "//", self.lineno, self.pos)
                    return self.get_next_token()
                elif self.char == '*':
                    self.state = None
                    self.__get_next_char()
                    return Token(Token.COMMENTSTART, "/*", self.lineno, self.pos)
                else:
                    self.state = None
                    return Token(Token.SLASH, "/", self.lineno, self.pos)
            case Token.ASSIGN:
                self.__get_next_char()
                if self.char == '=':
                    self.state = None
                    self.__get_next_char()
                    return Token(Token.EQ, "==", self.lineno, self.pos)
                else:
                    self.state = None
                    return Token(Token.ASSIGN, "=", self.lineno, self.pos)
            case Token.L:
                self.__get_next_char()
                if self.char == '=':
                    self.state = None
                    self.__get_next_char()
                    return Token(Token.LE, "<=", self.lineno, self.pos)
                elif self.char == '<':
                    self.state = None
                    self.__get_next_char()
                    return Token(Token.DL, "<<", self.lineno, self.pos)
                else:
                    self.state = None
                    return Token(Token.L, "<", self.lineno, self.pos)
            case Token.G:
                self.__get_next_char()
                if self.char == '=':
                    self.state = None
                    self.__get_next_char()
                    return Token(Token.GE, ">=", self.lineno, self.pos)
                elif self.char == '>':
                    self.state = None
                    self.__get_next_char()
                    return Token(Token.DG, ">>", self.lineno, self.pos)
                else:
                    self.state = None
                    return Token(Token.G, ">", self.lineno, self.pos)
            case Token.STRING_LITERAL_1:
                self.__get_next_char()
                string_literal_1 = ""
                while self.char != '"':
                    if self.char == '':  # если достигнут конец файла
                        self.error('Ожидалась закрывающая кавычка!')
                    string_literal_1 += self.char
                    self.__get_next_char()
                self.__get_next_char()
                self.state = None
                # self.pos минус 2 потому что токен оканчивается за 2 символа
                # до текущего положения чтения (оно сейчас указывает на символ
                # после кавычки, а не на последний символ строки)
                return Token(Token.STRING_LITERAL_1, string_literal_1, self.lineno, self.pos - 2)
            case Token.STRING_LITERAL_2:
                self.__get_next_char()
                string_literal_2 = ''
                while self.char != "'":
                    if self.char == '':  # если достигнут конец файла
                        self.error('Ожидалась закрывающая кавычка!')
                    string_literal_2 += self.char
                    self.__get_next_char()
                self.__get_next_char()
                self.state = None
                # self.pos минус 2 потому что токен оканчивается за 2 символа
                # до текущего положения чтения (оно сейчас указывает на символ
                # после кавычки, а не на последний символ строки)
                return Token(Token.STRING_LITERAL_2, string_literal_2, self.lineno, self.pos - 2)
            case Token.INT_LITERAL:
                int_literal = ""
                while self.char.isdigit():
                    int_literal += self.char
                    self.__get_next_char()
                if self.char == '.':
                    self.state = Token.FLOAT_LITERAL
                    float_literal = int_literal + '.'
                    self.__get_next_char()
                    while self.char.isdigit():
                        float_literal += self.char
                        self.__get_next_char()
                if self.char.isalpha() or self.char == '_':
                    self.error("Неверная запись идентификатора!")
                if self.state == Token.INT_LITERAL:
                    self.state = None
                    return Token(Token.INT_LITERAL, int_literal, self.lineno, self.pos - 1)
                if self.state == Token.FLOAT_LITERAL:
                    self.state = None
                    return Token(Token.FLOAT_LITERAL, float_literal, self.lineno, self.pos - 1)
            case Token.ID:
                id = self.char
                self.__get_next_char()
                while self.char.isalpha() or self.char.isdigit() or self.char == '_':
                    id += self.char
                    self.__get_next_char()
                self.state = None
                if id in Token.KEYWORDS:
                    return Token(Token.KEYWORDS[id], id, self.lineno, self.pos - 1)
                else:
                    return Token(Token.ID, id, self.lineno, self.pos - 1)
            case Token.AND:
                self.__get_next_char()
                if self.char == '&':
                    self.state = None
                    self.__get_next_char()
                    return Token(Token.AND, "&&", self.lineno, self.pos)
                else:
                    self.state = None
                    return Token(Token.LINK, "&", self.lineno, self.pos)
            case Token.OR:
                self.__get_next_char()
                if self.char == '|':
                    self.state = None
                    self.__get_next_char()
                    return Token(Token.OR, "||", self.lineno, self.pos)
            case Token.ASTERISK:
                self.__get_next_char()
                if self.char == '/':
                    self.state = None
                    self.__get_next_char()
                    return Token(Token.COMMENTEND, "/*", self.lineno, self.pos)
            case Token.DSLASH:

                self.__get_next_char()
                text = ''
                while self.char != '\n':
                    text += self.char
                    self.__get_next_char()
                self.state = None
                return Token(Token.DSLASH, text, self.lineno, self.pos - 1)



