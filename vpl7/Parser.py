import sys

from Expression import *
from Lexer import Token, TokenType

"""
This file implements the parser of logic and arithmetic expressions.

Precedence table:
    1: not ~ ()
    2: *   /
    3: +   -
    4: <   <=   >=   >
    5: =
    6: and
    7: or
    8: if-then-else

Notice that not 2 < 3 must be a type error, as we are trying to apply a boolean
operation (not) onto a number.

References:
    see https://www.engr.mun.ca/~theo/Misc/exp_parsing.htm#classic
"""

class Parser:
    def __init__(self, tokens):
        """
        Initializes the parser. The parser keeps track of the list of tokens
        and the current token. For instance:
        """
        self.tokens = list(tokens)
        self.cur_token_idx = 0 # This is just a suggestion!

    @property
    def current_token(self):
        if self.cur_token_idx < len(self.tokens):
            return self.tokens[self.cur_token_idx]
        return Token('', None)

    def advance(self):
        self.cur_token_idx += 1

    def eat(self, token_type):
        if self.current_token.kind == token_type:
            self.advance()
        else:
            raise ValueError(f"Unexpected token: {self.current_token.kind}, expected: {token_type}")

    def parse(self):
        """
        Returns the expression associated with the stream of tokens.

        Examples:
        >>> parser = Parser([Token('123', TokenType.NUM)])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        123

        >>> parser = Parser([Token('True', TokenType.TRU)])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        True

        >>> parser = Parser([Token('False', TokenType.FLS)])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        False

        >>> tk0 = Token('~', TokenType.NEG)
        >>> tk1 = Token('123', TokenType.NUM)
        >>> parser = Parser([tk0, tk1])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        -123

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        12

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('~', TokenType.NEG)
        >>> tk3 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        -12

        >>> tk0 = Token('30', TokenType.NUM)
        >>> tk1 = Token('/', TokenType.DIV)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        7

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('+', TokenType.ADD)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        7

        >>> tk0 = Token('30', TokenType.NUM)
        >>> tk1 = Token('-', TokenType.SUB)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        26

        >>> tk0 = Token('2', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('(', TokenType.LPR)
        >>> tk3 = Token('3', TokenType.NUM)
        >>> tk4 = Token('+', TokenType.ADD)
        >>> tk5 = Token('4', TokenType.NUM)
        >>> tk6 = Token(')', TokenType.RPR)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        14

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('==', TokenType.EQL)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        True

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('<=', TokenType.LEQ)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        True

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('<', TokenType.LTH)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        False

        >>> tk0 = Token('not', TokenType.NOT)
        >>> tk1 = Token('(', TokenType.LPR)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> tk3 = Token('<', TokenType.LTH)
        >>> tk4 = Token('4', TokenType.NUM)
        >>> tk5 = Token(')', TokenType.RPR)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        True

        >>> tk0 = Token('true', TokenType.TRU)
        >>> tk1 = Token('or', TokenType.ORX)
        >>> tk2 = Token('false', TokenType.FLS)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        True

        >>> tk0 = Token('true', TokenType.TRU)
        >>> tk1 = Token('and', TokenType.AND)
        >>> tk2 = Token('false', TokenType.FLS)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        False

        >>> tk0 = Token('let', TokenType.LET)
        >>> tk1 = Token('v', TokenType.VAR)
        >>> tk2 = Token('<-', TokenType.ASN)
        >>> tk3 = Token('42', TokenType.NUM)
        >>> tk4 = Token('in', TokenType.INX)
        >>> tk5 = Token('v', TokenType.VAR)
        >>> tk6 = Token('end', TokenType.END)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, {})
        42

        >>> tk0 = Token('let', TokenType.LET)
        >>> tk1 = Token('v', TokenType.VAR)
        >>> tk2 = Token('<-', TokenType.ASN)
        >>> tk3 = Token('21', TokenType.NUM)
        >>> tk4 = Token('in', TokenType.INX)
        >>> tk5 = Token('v', TokenType.VAR)
        >>> tk6 = Token('+', TokenType.ADD)
        >>> tk7 = Token('v', TokenType.VAR)
        >>> tk8 = Token('end', TokenType.END)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6, tk7, tk8])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, {})
        42

        >>> tk0 = Token('if', TokenType.IFX)
        >>> tk1 = Token('2', TokenType.NUM)
        >>> tk2 = Token('<', TokenType.LTH)
        >>> tk3 = Token('3', TokenType.NUM)
        >>> tk4 = Token('then', TokenType.THN)
        >>> tk5 = Token('1', TokenType.NUM)
        >>> tk6 = Token('else', TokenType.ELS)
        >>> tk7 = Token('2', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6, tk7])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        1

        >>> tk0 = Token('if', TokenType.IFX)
        >>> tk1 = Token('false', TokenType.FLS)
        >>> tk2 = Token('then', TokenType.THN)
        >>> tk3 = Token('1', TokenType.NUM)
        >>> tk4 = Token('else', TokenType.ELS)
        >>> tk5 = Token('2', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        2
        """
        return self.G_condicional()

    def G_condicional(self):
        if self.current_token.kind == TokenType.IFX:
            self.eat(TokenType.IFX)
            cond = self.G_condicional()
            self.eat(TokenType.THN)
            then_branch = self.G_condicional()
            self.eat(TokenType.ELS)
            else_branch = self.G_condicional()
            return IfThenElse(cond, then_branch, else_branch)
        else:
            return self.G_logico()

    def G_logico(self):
        exp = self.G_igualdade()
        while self.current_token.kind in (TokenType.ORX, TokenType.AND):
            if self.current_token.kind == TokenType.ORX:
                self.eat(TokenType.ORX)
                exp = Or(exp, self.G_igualdade())
            elif self.current_token.kind == TokenType.AND:
                self.eat(TokenType.AND)
                exp = And(exp, self.G_igualdade())
        return exp

    def G_igualdade(self):
        exp = self.G_comparacao()
        while self.current_token.kind == TokenType.EQL:
            self.eat(TokenType.EQL)
            right = self.G_comparacao()
            exp = Eql(exp, right)
        return exp

    def G_comparacao(self):
        exp = self.G_termo()
        while self.current_token.kind in (TokenType.LEQ, TokenType.LTH):
            if self.current_token.kind == TokenType.LEQ:
                self.eat(TokenType.LEQ)
                right = self.G_termo()
                exp = Leq(exp, right)
            elif self.current_token.kind == TokenType.LTH:
                self.eat(TokenType.LTH)
                right = self.G_termo()
                exp = Lth(exp, right)
        return exp

    def G_termo(self):
        exp = self.G_fator()
        while self.current_token.kind in (TokenType.ADD, TokenType.SUB):
            if self.current_token.kind == TokenType.ADD:
                self.eat(TokenType.ADD)
                right = self.G_fator()
                exp = Add(exp, right)
            elif self.current_token.kind == TokenType.SUB:
                self.eat(TokenType.SUB)
                right = self.G_fator()
                exp = Sub(exp, right)
        return exp

    def G_fator(self):
        exp = self.G_unario()
        while self.current_token.kind in (TokenType.MUL, TokenType.DIV):
            if self.current_token.kind == TokenType.MUL:
                self.eat(TokenType.MUL)
                right = self.G_unario()
                exp = Mul(exp, right)
            elif self.current_token.kind == TokenType.DIV:
                self.eat(TokenType.DIV)
                right = self.G_unario()
                exp = Div(exp, right)
        return exp
    
    def G_unario(self):
        if self.current_token.kind == TokenType.NEG:
            self.eat(TokenType.NEG)
            return Neg(self.G_unario())
        elif self.current_token.kind == TokenType.NOT:
            self.eat(TokenType.NOT)
            return Not(self.G_atomo())
        else:
            return self.G_atomo()
    
    def G_atomo(self):
        token = self.current_token
        if token.kind == TokenType.NUM:
            self.eat(TokenType.NUM)
            return Num(int(token.text))
        elif token.kind == TokenType.TRU:
            self.eat(TokenType.TRU)
            return Bln(True)
        elif token.kind == TokenType.FLS:
            self.eat(TokenType.FLS)
            return Bln(False)
        elif token.kind == TokenType.VAR:
            self.eat(TokenType.VAR)
            return Var(token.text)
        elif token.kind == TokenType.LPR:
            self.eat(TokenType.LPR)
            expr = self.G_condicional()
            self.eat(TokenType.RPR)
            return expr
        elif token.kind == TokenType.LET:
            self.eat(TokenType.LET)
            var_token = self.current_token
            self.eat(TokenType.VAR)
            self.eat(TokenType.ASN)
            var_expr = self.G_condicional()
            self.eat(TokenType.INX)
            in_expr = self.G_condicional()
            self.eat(TokenType.END)
            return Let(var_token.text, var_expr, in_expr)
        else:
            raise ValueError(f"Parse error")