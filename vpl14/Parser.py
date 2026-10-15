import sys

from Expression import *
from Lexer import Token, TokenType

"""
This file implements a parser for SML with anonymous functions. The grammar is
as follows:

fn_exp  ::= fn <var> => fn_exp
          | if_exp
if_exp  ::= <if> if_exp <then> fn_exp <else> fn_exp
          | or_exp
or_exp  ::= and_exp (or and_exp)*
and_exp ::= eq_exp (and eq_exp)*
eq_exp  ::= cmp_exp (= cmp_exp)*
cmp_exp ::= add_exp ([<=|<] add_exp)*
add_exp ::= mul_exp ([+|-] mul_exp)*
mul_exp ::= unary_exp ([*|/] unary_exp)*
unary_exp ::= <not> unary_exp
             | ~ unary_exp
             | let_exp
let_exp ::= <let> <var> <- fn_exp <in> fn_exp <end>
          | val_exp
val_exp ::= val_tk (val_tk)*
val_tk ::= <var> | ( fn_exp ) | <num> | <true> | <false>

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
        self.cur_token_idx = 0
    
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
            raise ValueError(f"Expected {token_type}, got {self.current_token.kind}")

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

        >>> tk0 = Token('fn', TokenType.FNX)
        >>> tk1 = Token('v', TokenType.VAR)
        >>> tk2 = Token('=>', TokenType.ARW)
        >>> tk3 = Token('v', TokenType.VAR)
        >>> tk4 = Token('+', TokenType.ADD)
        >>> tk5 = Token('1', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> print(exp.accept(ev, None))
        Fn(v)

        >>> tk0 = Token('(', TokenType.LPR)
        >>> tk1 = Token('fn', TokenType.FNX)
        >>> tk2 = Token('v', TokenType.VAR)
        >>> tk3 = Token('=>', TokenType.ARW)
        >>> tk4 = Token('v', TokenType.VAR)
        >>> tk5 = Token('+', TokenType.ADD)
        >>> tk6 = Token('1', TokenType.NUM)
        >>> tk7 = Token(')', TokenType.RPR)
        >>> tk8 = Token('2', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6, tk7, tk8])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, {})
        3
        """
        return self.fn_exp()
    
    def fn_exp(self):
        """fn_exp ::= fn <var> => fn_exp | if_exp"""
        if self.current_token.kind == TokenType.FNX:
            self.eat(TokenType.FNX)
            var_name = self.current_token.text
            self.eat(TokenType.VAR)
            self.eat(TokenType.ARW)
            body = self.fn_exp()
            return Fn(var_name, body)
        else:
            return self.if_exp()
    
    def if_exp(self):
        """if_exp ::= <if> if_exp <then> fn_exp <else> fn_exp | or_exp"""
        if self.current_token.kind == TokenType.IFX:
            self.eat(TokenType.IFX)
            cond = self.if_exp()
            self.eat(TokenType.THN)
            then_branch = self.fn_exp()
            self.eat(TokenType.ELS)
            else_branch = self.fn_exp()
            return IfThenElse(cond, then_branch, else_branch)
        else:
            return self.or_exp()
    
    def or_exp(self):
        """or_exp ::= and_exp (or and_exp)*"""
        expr = self.and_exp()
        while self.current_token.kind == TokenType.ORX:
            self.eat(TokenType.ORX)
            right = self.and_exp()
            expr = Or(expr, right)
        return expr
    
    def and_exp(self):
        """and_exp ::= eq_exp (and eq_exp)*"""
        expr = self.eq_exp()
        while self.current_token.kind == TokenType.AND:
            self.eat(TokenType.AND)
            right = self.eq_exp()
            expr = And(expr, right)
        return expr
    
    def eq_exp(self):
        """eq_exp ::= cmp_exp (= cmp_exp)*"""
        expr = self.cmp_exp()
        while self.current_token.kind == TokenType.EQL:
            self.eat(TokenType.EQL)
            right = self.cmp_exp()
            expr = Eql(expr, right)
        return expr
    
    def cmp_exp(self):
        """cmp_exp ::= add_exp ([<=|<] add_exp)*"""
        expr = self.add_exp()
        while self.current_token.kind in (TokenType.LEQ, TokenType.LTH):
            if self.current_token.kind == TokenType.LEQ:
                self.eat(TokenType.LEQ)
                right = self.add_exp()
                expr = Leq(expr, right)
            elif self.current_token.kind == TokenType.LTH:
                self.eat(TokenType.LTH)
                right = self.add_exp()
                expr = Lth(expr, right)
        return expr
    
    def add_exp(self):
        """add_exp ::= mul_exp ([+|-] mul_exp)*"""
        expr = self.mul_exp()
        while self.current_token.kind in (TokenType.ADD, TokenType.SUB):
            if self.current_token.kind == TokenType.ADD:
                self.eat(TokenType.ADD)
                right = self.mul_exp()
                expr = Add(expr, right)
            elif self.current_token.kind == TokenType.SUB:
                self.eat(TokenType.SUB)
                right = self.mul_exp()
                expr = Sub(expr, right)
        return expr
    
    def mul_exp(self):
        """mul_exp ::= unary_exp ([*|/] unary_exp)*"""
        expr = self.unary_exp()
        while self.current_token.kind in (TokenType.MUL, TokenType.DIV):
            if self.current_token.kind == TokenType.MUL:
                self.eat(TokenType.MUL)
                right = self.unary_exp()
                expr = Mul(expr, right)
            elif self.current_token.kind == TokenType.DIV:
                self.eat(TokenType.DIV)
                right = self.unary_exp()
                expr = Div(expr, right)
        return expr
    
    def unary_exp(self):
        """unary_exp ::= <not> unary_exp | ~ unary_exp | let_exp"""
        if self.current_token.kind == TokenType.NOT:
            self.eat(TokenType.NOT)
            expr = self.unary_exp()
            return Not(expr)
        elif self.current_token.kind == TokenType.NEG:
            self.eat(TokenType.NEG)
            expr = self.unary_exp()
            return Neg(expr)
        else:
            return self.let_exp()
    
    def let_exp(self):
        """let_exp ::= <let> <var> <- fn_exp <in> fn_exp <end> | val_exp"""
        if self.current_token.kind == TokenType.LET:
            self.eat(TokenType.LET)
            var_name = self.current_token.text
            self.eat(TokenType.VAR)
            self.eat(TokenType.ASN)
            var_value = self.fn_exp()
            self.eat(TokenType.INX)
            body = self.fn_exp()
            self.eat(TokenType.END)
            return Let(var_name, var_value, body)
        else:
            return self.val_exp()
    
    def val_exp(self):
        """val_exp ::= val_tk (val_tk)*"""
        expr = self.val_tk()
        
        # Handle function applications
        while self.current_token.kind in (TokenType.VAR, TokenType.LPR, 
                                          TokenType.NUM, TokenType.TRU, TokenType.FLS):
            arg = self.val_tk()
            expr = App(expr, arg)
        
        return expr
    
    def val_tk(self):
        """val_tk ::= <var> | ( fn_exp ) | <num> | <true> | <false>"""
        tok = self.current_token
        if tok.kind == TokenType.VAR:
            self.eat(TokenType.VAR)
            return Var(tok.text)
        elif tok.kind == TokenType.LPR:
            self.eat(TokenType.LPR)
            expr = self.fn_exp()
            self.eat(TokenType.RPR)
            return expr
        elif tok.kind == TokenType.NUM:
            self.eat(TokenType.NUM)
            return Num(int(tok.text))
        elif tok.kind == TokenType.TRU:
            self.eat(TokenType.TRU)
            return Bln(True)
        elif tok.kind == TokenType.FLS:
            self.eat(TokenType.FLS)
            return Bln(False)
        else:
            raise ValueError(f"Parse error")