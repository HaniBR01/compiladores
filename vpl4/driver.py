import sys
from Expression import *
from Lexer import Lexer
from Parser import Parser

if __name__ == "__main__":
    """
    Este arquivo nao deve ser alterado, mas deve ser enviado para resolver o
    VPL. O arquivo contem o codigo que testa a implementacao do parser.
    """
    lexer = Lexer(sys.stdin.read())
    parser = Parser(lexer.tokens())
    exp = parser.parse()
    print(f"Value is {exp.eval({})}")