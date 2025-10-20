import sys
from abc import ABC, abstractmethod
from Expression import *
from enum import Enum, auto

class Visitor(ABC):
    """
    The visitor pattern consists of two abstract classes: the Expression and the
    Visitor. The Expression class defines on method: 'accept(visitor, args)'.
    This method takes in an implementation of a visitor, and the arguments that
    are passed from expression to expression. The Visitor class defines one
    specific method for each subclass of Expression. Each instance of such a
    subclasse will invoke the right visiting method.
    """
    @abstractmethod
    def visit_var(self, exp, arg):
        pass

    @abstractmethod
    def visit_bln(self, exp, arg):
        pass

    @abstractmethod
    def visit_num(self, exp, arg):
        pass

    @abstractmethod
    def visit_eql(self, exp, arg):
        pass

    @abstractmethod
    def visit_and(self, exp, arg):
        pass

    @abstractmethod
    def visit_or(self, exp, arg):
        pass

    @abstractmethod
    def visit_add(self, exp, arg):
        pass

    @abstractmethod
    def visit_sub(self, exp, arg):
        pass

    @abstractmethod
    def visit_mul(self, exp, arg):
        pass

    @abstractmethod
    def visit_div(self, exp, arg):
        pass

    @abstractmethod
    def visit_leq(self, exp, arg):
        pass

    @abstractmethod
    def visit_lth(self, exp, arg):
        pass

    @abstractmethod
    def visit_neg(self, exp, arg):
        pass

    @abstractmethod
    def visit_not(self, exp, arg):
        pass

    @abstractmethod
    def visit_let(self, exp, arg):
        pass

    @abstractmethod
    def visit_ifThenElse(self, exp, arg):
        pass

class Type(Enum):
    INT = auto()
    BOOL = auto()

class TypeChecker(Visitor):
    """
    The TypeChecker class performs static type checking on expressions.
    It returns the type of each expression and verifies type compatibility.
    The environment maps variable names to their types.
    """
    
    def visit_var(self, exp, type_env):
        if exp.identifier not in type_env:
            msg = "Def error"
            sys.exit(msg)
        return type_env[exp.identifier]

    def visit_bln(self, exp, type_env):
        return Type.BOOL

    def visit_num(self, exp, type_env):
        return Type.INT

    def visit_eql(self, exp, type_env):
        t0 = exp.left.accept(self, type_env)
        t1 = exp.right.accept(self, type_env)
        if t0 != t1:
            msg = "Type error"
            sys.exit(msg)
        return Type.BOOL

    def visit_and(self, exp, type_env):
        t0 = exp.left.accept(self, type_env)
        t1 = exp.right.accept(self, type_env)
        self.ensure_type(t0, Type.BOOL, "and")
        self.ensure_type(t1, Type.BOOL, "and")
        return Type.BOOL

    def visit_or(self, exp, type_env):
        t0 = exp.left.accept(self, type_env)
        t1 = exp.right.accept(self, type_env)
        self.ensure_type(t0, Type.BOOL, "or")
        self.ensure_type(t1, Type.BOOL, "or")
        return Type.BOOL

    def visit_add(self, exp, type_env):
        t0 = exp.left.accept(self, type_env)
        t1 = exp.right.accept(self, type_env)
        self.ensure_type(t0, Type.INT, "add")
        self.ensure_type(t1, Type.INT, "add")
        return Type.INT

    def visit_sub(self, exp, type_env):
        t0 = exp.left.accept(self, type_env)
        t1 = exp.right.accept(self, type_env)
        self.ensure_type(t0, Type.INT, "sub")
        self.ensure_type(t1, Type.INT, "sub")
        return Type.INT

    def visit_mul(self, exp, type_env):
        t0 = exp.left.accept(self, type_env)
        t1 = exp.right.accept(self, type_env)
        self.ensure_type(t0, Type.INT, "mul")
        self.ensure_type(t1, Type.INT, "mul")
        return Type.INT

    def visit_div(self, exp, type_env):
        t0 = exp.left.accept(self, type_env)
        t1 = exp.right.accept(self, type_env)
        self.ensure_type(t0, Type.INT, "div")
        self.ensure_type(t1, Type.INT, "div")
        return Type.INT

    def visit_leq(self, exp, type_env):
        t0 = exp.left.accept(self, type_env)
        t1 = exp.right.accept(self, type_env)
        self.ensure_type(t0, Type.INT, "leq")
        self.ensure_type(t1, Type.INT, "leq")
        return Type.BOOL

    def visit_lth(self, exp, type_env):
        t0 = exp.left.accept(self, type_env)
        t1 = exp.right.accept(self, type_env)
        self.ensure_type(t0, Type.INT, "lth")
        self.ensure_type(t1, Type.INT, "lth")
        return Type.BOOL

    def visit_neg(self, exp, type_env):
        t0 = exp.exp.accept(self, type_env)
        self.ensure_type(t0, Type.INT, "neg")
        return Type.INT

    def visit_not(self, exp, type_env):
        t0 = exp.exp.accept(self, type_env)
        self.ensure_type(t0, Type.BOOL, "not")
        return Type.BOOL

    def visit_let(self, exp, type_env):
        var = exp.identifier
        t0 = exp.exp_def.accept(self, type_env)
        new_type_env = type_env.copy()
        new_type_env[var] = t0
        return exp.exp_body.accept(self, new_type_env)
        
    def visit_ifThenElse(self, exp, type_env):
        t_cond = exp.cond.accept(self, type_env)
        self.ensure_type(t_cond, Type.BOOL, "if")
        t0 = exp.e0.accept(self, type_env)
        t1 = exp.e1.accept(self, type_env)
        if t0 != t1:
            msg = "Type error"
            sys.exit(msg)
        return t0

    def ensure_type(self, runtime_type, expected_type, operation_name):
        if runtime_type != expected_type:
            msg = "Type error"
            sys.exit(msg)

class EvalVisitor(Visitor):
    """
    The EvalVisitor class evaluates logical and arithmetic expressions. The
    result of evaluating an expression is the value of that expression. The
    inherited attribute propagated throughout visits is the environment that
    associates the names of variables with values.
    
    Notice that this implementation must perform type verification. If some
    verification fail, then it invokes sys.exit with the correct error
    message. We expect two different messages:
    
    1. sys.exit("Type error")
    2. sys.exit("Def error")

    Examples:
    >>> e0 = Let('v', Add(Num(40), Num(2)), Mul(Var('v'), Var('v')))
    >>> e1 = Not(Eql(e0, Num(1764)))
    >>> ev = EvalVisitor()
    >>> e1.accept(ev, {})
    False

    >>> e0 = Let('v', Add(Num(40), Num(2)), Sub(Var('v'), Num(2)))
    >>> e1 = Lth(e0, Var('x'))
    >>> ev = EvalVisitor()
    >>> e1.accept(ev, {'x': 41})
    True
    """

    def __init__(self):
        self.type_checker = TypeChecker()

    def visit_var(self, exp, env):
        if exp.identifier not in env:
            msg = "Def error"
            sys.exit(msg)
        return env[exp.identifier]

    def visit_bln(self, exp, env):
        return exp.bln

    def visit_num(self, exp, env):
        return exp.num

    def visit_eql(self, exp, env):
        v0 = exp.left.accept(self, env)
        v1 = exp.right.accept(self, env)
        # Verificação de tipo: EQL requer tipos compatíveis
        if type(v0) != type(v1):
            msg = "Type error"
            sys.exit(msg)
        return v0 == v1

    def visit_and(self, exp, env):
        v0 = exp.left.accept(self, env)
        # Verificação de tipo: AND só aceita booleanos (não inteiros)
        if type(v0) is not bool:
            msg = "Type error"
            sys.exit(msg)
        if not v0:
            return False
        v1 = exp.right.accept(self, env)
        if type(v1) is not bool:
            msg = "Type error"
            sys.exit(msg)
        return v1

    def visit_or(self, exp, env):
        v0 = exp.left.accept(self, env)
        # Verificação de tipo: OR só aceita booleanos (não inteiros)
        if type(v0) is not bool:
            msg = "Type error"
            sys.exit(msg)
        if v0:
            return True
        v1 = exp.right.accept(self, env)
        if type(v1) is not bool:
            msg = "Type error"
            sys.exit(msg)
        return v1

    def visit_add(self, exp, env):
        v0 = exp.left.accept(self, env)
        v1 = exp.right.accept(self, env)
        # Verificação de tipo: ADD só aceita inteiros (não booleanos)
        if type(v0) is not int or type(v1) is not int:
            msg = "Type error"
            sys.exit(msg)
        return v0 + v1

    def visit_sub(self, exp, env):
        v0 = exp.left.accept(self, env)
        v1 = exp.right.accept(self, env)
        # Verificação de tipo: SUB só aceita inteiros (não booleanos)
        if type(v0) is not int or type(v1) is not int:
            msg = "Type error"
            sys.exit(msg)
        return v0 - v1

    def visit_mul(self, exp, env):
        v0 = exp.left.accept(self, env)
        v1 = exp.right.accept(self, env)
        # Verificação de tipo: MUL só aceita inteiros (não booleanos)
        if type(v0) is not int or type(v1) is not int:
            msg = "Type error"
            sys.exit(msg)
        return v0 * v1

    def visit_div(self, exp, env):
        v0 = exp.left.accept(self, env)
        v1 = exp.right.accept(self, env)
        # Verificação de tipo: DIV só aceita inteiros (não booleanos)
        if type(v0) is not int or type(v1) is not int:
            msg = "Type error"
            sys.exit(msg)
        if v1 == 0:
            msg = "1D"
            sys.exit(msg)
        return v0 // v1  # Divisão inteira

    def visit_leq(self, exp, env):
        v0 = exp.left.accept(self, env)
        v1 = exp.right.accept(self, env)
        # Verificação de tipo: LEQ só aceita inteiros (não booleanos)
        if type(v0) is not int or type(v1) is not int:
            msg = "Type error"
            sys.exit(msg)
        return v0 <= v1

    def visit_lth(self, exp, env):
        v0 = exp.left.accept(self, env)
        v1 = exp.right.accept(self, env)
        # Verificação de tipo: LTH só aceita inteiros (não booleanos)
        if type(v0) is not int or type(v1) is not int:
            msg = "Type error"
            sys.exit(msg)
        return v0 < v1

    def visit_neg(self, exp, env):
        v0 = exp.exp.accept(self, env)
        # Verificação de tipo: NEG só aceita inteiros (não booleanos)
        if type(v0) is not int:
            msg = "Type error"
            sys.exit(msg)
        return -v0

    def visit_not(self, exp, env):
        v0 = exp.exp.accept(self, env)
        # Verificação de tipo: NOT só aceita booleanos (não inteiros)
        if type(v0) is not bool:
            msg = "Type error"
            sys.exit(msg)
        return not v0

    def visit_let(self, exp, env):
        var = exp.identifier
        v0 = exp.exp_def.accept(self, env)
        new_env = env.copy() if env is not None else {}
        new_env[var] = v0
        return exp.exp_body.accept(self, new_env)
        
    def visit_ifThenElse(self, exp, env):
        v0 = exp.cond.accept(self, env)
        # Verificação de tipo: condição do IF deve ser booleana (não inteiro)
        if type(v0) is not bool:
            msg = "Type error"
            sys.exit(msg)
        if v0:
            return exp.e0.accept(self, env)
        return exp.e1.accept(self, env)

    # Método para fazer type checking + evaluation em uma só chamada
    def evaluate_with_type_check(self, expression, env):
        """
        Performs type checking followed by evaluation.
        Returns the evaluated result.
        """
        # Primeiro, extrai os tipos do ambiente para type checking
        type_env = {}
        for var, value in env.items():
            if isinstance(value, bool):
                type_env[var] = Type.BOOL
            elif isinstance(value, int):
                type_env[var] = Type.INT
        
        # Faz type checking
        result_type = expression.accept(self.type_checker, type_env)
        
        # Depois faz evaluation
        return expression.accept(self, env)
# End of EvalVisitor class