import sys
from Expression import *
from Visitor import *
from Lexer import Lexer
from Parser import Parser
import Asm as AsmModule

def rename_variables(exp):
    """
    Esta funcao invoca o renomeador de variaveis. Ela deve ser usada antes do
    inicio da fase de geracao de codigo.
    """
    ren = RenameVisitor()
    exp.accept(ren, {})
    return exp

if __name__ == "__main__":
    """
    Este arquivo nao deve ser alterado, mas deve ser enviado para resolver o
    VPL. O arquivo contem o codigo que testa a implementacao do parser.
    """
    text = sys.stdin.read()
    lexer = Lexer(text)
    parser = Parser(lexer.tokens())
    exp = rename_variables(parser.parse())
    prog = AsmModule.Program({}, [])
    gen = GenVisitor()
    var_answer = exp.accept(gen, prog)
    prog.eval()
    print(f"{prog.get_val(var_answer)}")