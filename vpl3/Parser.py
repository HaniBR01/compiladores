import sys

from Expression import *
from Lexer import Token, TokenType

"""
This file implements the parser of arithmetic expressions.

References:
    see https://www.engr.mun.ca/~theo/Misc/exp_parsing.htm
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
        >>> exp.eval()
        123

        >>> parser = Parser([Token('True', TokenType.TRU)])
        >>> exp = parser.parse()
        >>> exp.eval()
        True

        >>> parser = Parser([Token('False', TokenType.FLS)])
        >>> exp = parser.parse()
        >>> exp.eval()
        False

        >>> tk0 = Token('~', TokenType.NEG)
        >>> tk1 = Token('123', TokenType.NUM)
        >>> parser = Parser([tk0, tk1])
        >>> exp = parser.parse()
        >>> exp.eval()
        -123

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> exp.eval()
        12

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('~', TokenType.NEG)
        >>> tk3 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3])
        >>> exp = parser.parse()
        >>> exp.eval()
        -12

        >>> tk0 = Token('30', TokenType.NUM)
        >>> tk1 = Token('/', TokenType.DIV)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> exp.eval()
        7

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('+', TokenType.ADD)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> exp.eval()
        7

        >>> tk0 = Token('30', TokenType.NUM)
        >>> tk1 = Token('-', TokenType.SUB)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> exp.eval()
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
        >>> exp.eval()
        14

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('==', TokenType.EQL)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> exp.eval()
        True

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('<=', TokenType.LEQ)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> exp.eval()
        True

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('<', TokenType.LTH)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> exp.eval()
        False

        >>> tk0 = Token('not', TokenType.NOT)
        >>> tk1 = Token('4', TokenType.NUM)
        >>> tk2 = Token('<', TokenType.LTH)
        >>> tk3 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3])
        >>> exp = parser.parse()
        >>> exp.eval()
        True
        """
        return self.G_exp()

    def G_exp(self):
        if self.current_token.kind == TokenType.NOT:
            self.eat(TokenType.NOT)
            expr = self.G_exp()
            return Not(expr)
        else:
            return self.G_igualdade()

    def G_igualdade(self):
        expr = self.G_comparacao()
        while self.current_token.kind == TokenType.EQL:
            self.eat(TokenType.EQL)
            right = self.G_comparacao()
            expr = Eql(expr, right)
        return expr

    def G_comparacao(self):
        expr = self.G_termo()
        while self.current_token.kind in (TokenType.LEQ, TokenType.LTH):
            if self.current_token.kind == TokenType.LEQ:
                self.eat(TokenType.LEQ)
                right = self.G_termo()
                expr = Leq(expr, right)
            elif self.current_token.kind == TokenType.LTH:
                self.eat(TokenType.LTH)
                right = self.G_termo()
                expr = Lth(expr, right)
        return expr

    def G_termo(self):
        expr = self.G_fator()
        while self.current_token.kind in (TokenType.ADD, TokenType.SUB):
            if self.current_token.kind == TokenType.ADD:
                self.eat(TokenType.ADD)
                right = self.G_fator()
                expr = Add(expr, right)
            elif self.current_token.kind == TokenType.SUB:
                self.eat(TokenType.SUB)
                right = self.G_fator()
                expr = Sub(expr, right)
        return expr

    def G_fator(self):
        expr = self.G_unario()
        while self.current_token.kind in (TokenType.MUL, TokenType.DIV):
            if self.current_token.kind == TokenType.MUL:
                self.eat(TokenType.MUL)
                right = self.G_unario()
                expr = Mul(expr, right)
            elif self.current_token.kind == TokenType.DIV:
                self.eat(TokenType.DIV)
                right = self.G_unario()
                expr = Div(expr, right)
        return expr

    def G_unario(self):
        if self.current_token.kind == TokenType.NEG:
            self.eat(TokenType.NEG)
            expr = self.G_unario()
            return Neg(expr)
        else:
            return self.G_primario()

    def G_primario(self):
        tok = self.current_token
        if tok.kind == TokenType.NUM:
            self.eat(TokenType.NUM)
            return Num(int(tok.text))
        elif tok.kind == TokenType.TRU:
            self.eat(TokenType.TRU)
            return Bln(True)
        elif tok.kind == TokenType.FLS:
            self.eat(TokenType.FLS)
            return Bln(False)
        elif tok.kind == TokenType.LPR:
            self.eat(TokenType.LPR)
            expr = self.G_exp()
            self.eat(TokenType.RPR)
            return expr
        else:
            raise ValueError(f"Unexpected token in primary: {tok.kind}")