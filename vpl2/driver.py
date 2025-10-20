import sys
from Expression import *

if __name__ == "__main__":
    """
    Este arquivo nao deve ser alterado, mas deve ser enviado para resolver o
    VPL. O arquivo contem o codigo que testa a implementacao do analisador
    lexico.
    """
    e = eval(sys.stdin.read())
    print(f"Value is {e.eval()}")