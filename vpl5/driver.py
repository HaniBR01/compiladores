import sys
from Expression import *
from Visitor import *
from Lexer import Lexer
from Parser import Parser

if __name__ == "__main__":
    """
    Este arquivo nao deve ser alterado, mas deve ser enviado para resolver o
    VPL. O arquivo contem o codigo que testa a implementacao do parser.
    """
    text = sys.stdin.read()
    (option, rest) = text.split(maxsplit=1)
    lexer = Lexer(rest)
    parser = Parser(lexer.tokens())
    exp = parser.parse()
    if option == 'eval':
        visitor = EvalVisitor()
        print(f"Value is {exp.accept(visitor, {})}")
    elif option == 'usedef':
        visitor = UseDefVisitor()
        print(f"Are there undefs? {len(exp.accept(visitor, set())) > 0}")
    elif option == 'safe_eval':
        safe_eval(exp)
    else:
        sys.exit(f"Invalid option = {option}")