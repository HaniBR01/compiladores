import sys
from Lexer import *

if __name__ == "__main__":
    """
    Este arquivo nao deve ser alterado, mas deve ser enviado para resolver o
    VPL. O arquivo contem o codigo que testa a implementacao do analisador
    lexico.
    """
    lexer = Lexer(sys.stdin.read())
    for token in lexer.tokens():
        print(f"{token.kind.name}")