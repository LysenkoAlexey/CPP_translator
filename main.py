from lexer import Lexer, Token
from parser import Parser

with open("file.cpp", 'r', encoding='utf8') as f:
    lex = Lexer(f.read())
    pars = Parser(lex)
    #

# Вывод лексера
with open("file.cpp", 'r', encoding='utf8') as f:

    lex = Lexer(f.read())
t = lex.get_next_token()
while t.name != Token.EOF:
     print(t)
     t = lex.get_next_token()
print(t)



ast = pars.parse()

print(ast)
