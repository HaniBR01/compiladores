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
mul_exp ::= unary_exp ([*|div|mod] unary_exp)*
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
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> parser = Parser([Token('True', TokenType.TRU)])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> parser = Parser([Token('False', TokenType.FLS)])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> tk0 = Token('~', TokenType.NEG)
        >>> tk1 = Token('123', TokenType.NUM)
        >>> parser = Parser([tk0, tk1])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('~', TokenType.NEG)
        >>> tk3 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('30', TokenType.NUM)
        >>> tk1 = Token('/', TokenType.DIV)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('+', TokenType.ADD)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('30', TokenType.NUM)
        >>> tk1 = Token('-', TokenType.SUB)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('2', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('(', TokenType.LPR)
        >>> tk3 = Token('3', TokenType.NUM)
        >>> tk4 = Token('+', TokenType.ADD)
        >>> tk5 = Token('4', TokenType.NUM)
        >>> tk6 = Token(')', TokenType.RPR)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('==', TokenType.EQL)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('<=', TokenType.LEQ)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('<', TokenType.LTH)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> tk0 = Token('not', TokenType.NOT)
        >>> tk1 = Token('(', TokenType.LPR)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> tk3 = Token('<', TokenType.LTH)
        >>> tk4 = Token('4', TokenType.NUM)
        >>> tk5 = Token(')', TokenType.RPR)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> tk0 = Token('true', TokenType.TRU)
        >>> tk1 = Token('or', TokenType.ORX)
        >>> tk2 = Token('false', TokenType.FLS)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> tk0 = Token('true', TokenType.TRU)
        >>> tk1 = Token('and', TokenType.AND)
        >>> tk2 = Token('false', TokenType.FLS)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> t0 = Token('let', TokenType.LET)
        >>> t1 = Token('v', TokenType.VAR)
        >>> t2 = Token(':', TokenType.COL)
        >>> t3 = Token('int', TokenType.INT)
        >>> t4 = Token('<-', TokenType.ASN)
        >>> t5 = Token('42', TokenType.NUM)
        >>> t6 = Token('in', TokenType.INX)
        >>> t7 = Token('v', TokenType.VAR)
        >>> t8 = Token('end', TokenType.END)
        >>> parser = Parser([t0, t1, t2, t3, t4, t5, t6, t7, t8])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, {})
        <class 'int'>

        >>> t0 = Token('let', TokenType.LET)
        >>> t1 = Token('v', TokenType.VAR)
        >>> t2 = Token(':', TokenType.COL)
        >>> t3 = Token('int', TokenType.INT)
        >>> t4 = Token('<-', TokenType.ASN)
        >>> t5 = Token('21', TokenType.NUM)
        >>> t6 = Token('in', TokenType.INX)
        >>> t7 = Token('v', TokenType.VAR)
        >>> t8 = Token('+', TokenType.ADD)
        >>> t9 = Token('v', TokenType.VAR)
        >>> tA = Token('end', TokenType.END)
        >>> parser = Parser([t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, tA])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, {})
        <class 'int'>

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
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('if', TokenType.IFX)
        >>> tk1 = Token('false', TokenType.FLS)
        >>> tk2 = Token('then', TokenType.THN)
        >>> tk3 = Token('1', TokenType.NUM)
        >>> tk4 = Token('else', TokenType.ELS)
        >>> tk5 = Token('2', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('fn', TokenType.FNX)
        >>> tk1 = Token('v', TokenType.VAR)
        >>> tk2 = Token(':', TokenType.COL)
        >>> tk3 = Token('int', TokenType.INT)
        >>> tk4 = Token('=>', TokenType.ARW)
        >>> tk5 = Token('v', TokenType.VAR)
        >>> tk6 = Token('+', TokenType.ADD)
        >>> tk7 = Token('1', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6, tk7])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> print(exp.accept(ev, {}))
        <class 'int'> -> <class 'int'>

        >>> t0 = Token('(', TokenType.LPR)
        >>> t1 = Token('fn', TokenType.FNX)
        >>> t2 = Token('v', TokenType.VAR)
        >>> t3 = Token(':', TokenType.COL)
        >>> t4 = Token('int', TokenType.INT)
        >>> t5 = Token('=>', TokenType.ARW)
        >>> t6 = Token('v', TokenType.VAR)
        >>> t7 = Token('+', TokenType.ADD)
        >>> t8 = Token('1', TokenType.NUM)
        >>> t9 = Token(')', TokenType.RPR)
        >>> tA = Token('2', TokenType.NUM)
        >>> parser = Parser([t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, tA])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, {})
        <class 'int'>
        """
        return self.G_anonimo()

    def G_anonimo(self):
        if self.current_token.kind == TokenType.FNX:
            self.eat(TokenType.FNX)
            var_token = self.current_token
            self.eat(TokenType.VAR)
            self.eat(TokenType.COL)
            var_type = self.G_types()
            self.eat(TokenType.ARW)
            body = self.G_anonimo()
            return Fn(var_token.text, var_type, body)
        else:
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
            return Not(self.G_unario())
        else:
            return self.G_let_exp()

    def G_let_exp(self):
        if self.current_token.kind == TokenType.LET:
            
            self.eat(TokenType.LET)
            
            var_token = self.current_token
            var_name = var_token.text
            self.eat(TokenType.VAR)
            
            self.eat(TokenType.COL)

            var_type = self.G_types()

            self.eat(TokenType.ASN)
            
            var_expr = self.G_anonimo()
            
            self.eat(TokenType.INX)
            
            in_expr = self.G_anonimo()
            
            self.eat(TokenType.END)

            return Let(var_name, var_type, var_expr, in_expr)

        else:
            return self.G_val_exp()
    
    def G_val_exp(self):
        # Parse the first value token
        exp = self.G_val_tk()
        
        # Parse additional value tokens for function application
        while self.current_token.kind in (TokenType.VAR, TokenType.LPR, TokenType.NUM, TokenType.TRU, TokenType.FLS):
            arg = self.G_val_tk()
            exp = App(exp, arg)
        
        return exp
    
    def G_val_tk(self):
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
            expr = self.G_anonimo()
            self.eat(TokenType.RPR)
            return expr
        else:
            raise ValueError(f"Parse error: unexpected token {token.kind}")
        
    def G_types(self):
        token = self.G_type()
        if self.current_token.kind == TokenType.TPF:
            self.eat(TokenType.TPF)
            right_type = self.G_types()
            token = (token, right_type)
        return token
        
    def G_type(self):
        token = self.current_token
        if token.kind == TokenType.INT:
            self.eat(TokenType.INT)
            return type(1)
        elif token.kind == TokenType.LGC:
            self.eat(TokenType.LGC)
            return type(True)
        if token.kind == TokenType.LPR:
            self.eat(TokenType.LPR)
            types = self.G_types()
            self.eat(TokenType.RPR)
            return types
        else:
            raise ValueError(f"Parse error: unexpected type token {token.kind}")