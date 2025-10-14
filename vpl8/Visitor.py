import sys
from abc import ABC, abstractmethod
from vpl6.Expression import *
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

class Function():
    """
    This is the class that represents functions. This class lets us distinguish
    the three types that now exist in the language: numbers, booleans and
    functions. Notice that the evaluation of an expression can now be a
    function. For instance:

        >>> f = Fn('v', Mul(Var('v'), Var('v')))
        >>> ev = EvalVisitor()
        >>> fval = f.accept(ev, {})
        >>> type(fval)
        <class 'Visitor.Function'>
    """
    def __init__(self, formal, body, env):
        self.formal = formal
        self.body = body
        self.env = env
    def __str__(self):
        return f"Fn({self.formal})"
        

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
        if type(v0) == type(v1):
            return v0 == v1
        else:
            msg = "Type error"
            sys.exit(msg)

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
    
    def visit_fn(self, exp, env): # Implemented for you :)
        """
        The evaluation of a function is the function itself. Remember: in our
        language, functions are values as well. So, now we have three kinds of
        values: numbers, booleans and functions.
        """
        return Function(exp.formal, exp.body, env)

    def visit_app(self, exp, env):
        """
        Here comes most of the complexity of the homework, in five or six lines
        of code! You must implement the evaluation of a function application.
        """
        # TODO: Implement this method.
        raise NotImplementedException

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

class CtrGenVisitor(Visitor):
    """
    This visitor creates constraints for a type-inference engine. Basically,
    it traverses the abstract-syntax tree of expressions, producing pairs like
    (type0, type1) on the way. A pair like (type0, type1) indicates that these
    two type variables are the same.

    Examples:
        >>> e = Let('v', Num(40), Let('w', Num(2), Add(Var('v'), Var('w'))))
        >>> ev = CtrGenVisitor()
        >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
        ["('TV_1', 'TV_2')", "('TV_2', 'TV_3')", "('v', <class 'int'>)", "('w', <class 'int'>)", "(<class 'int'>, 'TV_3')", "(<class 'int'>, 'v')", "(<class 'int'>, 'w')"]
    """

    def __init__(self):
        self.fresh_type_counter = 0

    def fresh_type_var(self):
        """
        Create a new type var using the current value of the fresh_type_counter.
        Two successive calls to this method will return different type names.
        Notice that the name of a type variable is always TV_x, where x is
        some integer number. That means that probably we would run into
        errors if someone declares a variable called, say, TV_1 or TV_2, as in
        "let TV_1 <- 1 in TV_1 end". But you can assume that such would never
        happen in the test cases. In practice, we should define a new class
        to represent type variables. But let's keep the implementation as
        simple as possible.

        Example:
            >>> ev = CtrGenVisitor()
            >>> [ev.fresh_type_var(), ev.fresh_type_var()]
            ['TV_1', 'TV_2']
        """
        self.fresh_type_counter += 1
        return f"TV_{self.fresh_type_counter}"

    """
    The CtrGenVisitor class creates constraints that, once solved, will give
    us the type of the different variables. Every accept method takes in
    two arguments (in addition to self):
    
    exp: is the expression that is being analyzed.
    type_var: that is a name that works as a placeholder for the type of the
    expression. Whenever we visit a new expression, we create a type variable
    to represent its type (you can do that with the method fresh_type_var).
    The only exception is the type of Var expressions. In this case, the type
    of a Var expression is the identifier of that expression.
    """

    def visit_var(self, exp, type_var):
        """
        Example:
            >>> e = Var('v')
            >>> ev = CtrGenVisitor()
            >>> e.accept(ev, ev.fresh_type_var())
            {('v', 'TV_1')}
        """
        return {(exp.identifier, type_var)}

    def visit_bln(self, exp, type_var):
        """
        Example:
            >>> e = Bln(True)
            >>> ev = CtrGenVisitor()
            >>> e.accept(ev, ev.fresh_type_var())
            {(<class 'bool'>, 'TV_1')}
        """
        return {(type(True), type_var)}

    def visit_num(self, exp, type_var):
        """
        Example:
            >>> e = Num(1)
            >>> ev = CtrGenVisitor()
            >>> e.accept(ev, ev.fresh_type_var())
            {(<class 'int'>, 'TV_1')}
        """
        return {(type(1), type_var)}

    def visit_eql(self, exp, type_var):
        """
        Example:
            >>> e = Eql(Num(1), Bln(True))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'bool'>, 'TV_1')", "(<class 'bool'>, 'TV_2')", "(<class 'int'>, 'TV_2')"]

        Notice that if we have repeated constraints, they only appear once in
        the set of constraints (after all, it's a set!). As an example, we
        would have two occurrences of the pair (TV_2, int) in the following
        example:
            >>> e = Eql(Num(1), Num(2))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'bool'>, 'TV_1')", "(<class 'int'>, 'TV_2')"]
        """
        fresh_type_var = self.fresh_type_var()
        constraints_left = exp.left.accept(self, fresh_type_var)
        constraints_right = exp.right.accept(self, fresh_type_var)
        return constraints_left | constraints_right | {(type(True), type_var)}

    def visit_and(self, exp, type_var):
        """
        Example:
            >>> e = And(Bln(False), Bln(True))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'bool'>, 'TV_1')", "(<class 'bool'>, <class 'bool'>)"]

        In the above example, notice that we ended up getting a trivial
        constraint, e.g.: (<class 'bool'>, <class 'bool'>). That's alright:
        don't worry about these trivial constraints at this point. We can
        remove them from the set of constraints later on, when we try to
        solve them.
        """
        constraints_left = exp.left.accept(self, type(True))
        constraints_right = exp.right.accept(self, type(True))
        return constraints_left | constraints_right | {(type(True), type_var)}

    def visit_or(self, exp, type_var):
        """
        Example:
            >>> e = Or(Bln(False), Bln(True))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'bool'>, 'TV_1')", "(<class 'bool'>, <class 'bool'>)"]
        """
        constraints_left = exp.left.accept(self, type(True))
        constraints_right = exp.right.accept(self, type(True))
        return constraints_left | constraints_right | {(type(True), type_var)}

    def visit_add(self, exp, type_var):
        """
        Example:
            >>> e = Add(Num(1), Num(2))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'int'>, 'TV_1')", "(<class 'int'>, <class 'int'>)"]
        """
        constraints_left = exp.left.accept(self, type(1))
        constraints_right = exp.right.accept(self, type(1))
        return constraints_left | constraints_right | {(type(1), type_var)}

    def visit_sub(self, exp, type_var):
        """
        Example:
            >>> e = Sub(Num(1), Num(2))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'int'>, 'TV_1')", "(<class 'int'>, <class 'int'>)"]
        """
        constraints_left = exp.left.accept(self, type(1))
        constraints_right = exp.right.accept(self, type(1))
        return constraints_left | constraints_right | {(type(1), type_var)}

    def visit_mul(self, exp, type_var):
        """
        Example:
            >>> e = Mul(Num(1), Num(2))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'int'>, 'TV_1')", "(<class 'int'>, <class 'int'>)"]
        """
        constraints_left = exp.left.accept(self, type(1))
        constraints_right = exp.right.accept(self, type(1))
        return constraints_left | constraints_right | {(type(1), type_var)}

    def visit_div(self, exp, type_var):
        """
        Example:
            >>> e = Div(Num(1), Num(2))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'int'>, 'TV_1')", "(<class 'int'>, <class 'int'>)"]
        """
        constraints_left = exp.left.accept(self, type(1))
        constraints_right = exp.right.accept(self, type(1))
        return constraints_left | constraints_right | {(type(1), type_var)}

    def visit_leq(self, exp, type_var):
        """
        Example:
            >>> e = Leq(Num(1), Num(2))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'bool'>, 'TV_1')", "(<class 'int'>, <class 'int'>)"]
        """
        constraints_left = exp.left.accept(self, type(1))
        constraints_right = exp.right.accept(self, type(1))
        return constraints_left | constraints_right | {(type(True), type_var)}

    def visit_lth(self, exp, type_var):
        """
        Example:
            >>> e = Lth(Num(1), Num(2))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'bool'>, 'TV_1')", "(<class 'int'>, <class 'int'>)"]
        """
        constraints_left = exp.left.accept(self, type(1))
        constraints_right = exp.right.accept(self, type(1))
        return constraints_left | constraints_right | {(type(True), type_var)}

    def visit_neg(self, exp, type_var):
        """
        Example:
            >>> e = Neg(Num(1))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'int'>, 'TV_1')", "(<class 'int'>, <class 'int'>)"]
        """
        constraints = exp.exp.accept(self, type(1))
        return constraints | {(type(1), type_var)}

    def visit_not(self, exp, type_var):
        """
        Example:
            >>> e = Not(Bln(True))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'bool'>, 'TV_1')", "(<class 'bool'>, <class 'bool'>)"]
        """
        constraints = exp.exp.accept(self, type(True))
        return constraints | {(type(True), type_var)}

    def visit_let(self, exp, type_var):
        """
        Example:
            >>> e = Let('v', Num(42), Var('v'))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["('TV_1', 'TV_2')", "('v', 'TV_2')", "(<class 'int'>, 'v')"]
        """
        constraints_def = exp.exp_def.accept(self, exp.identifier)
        fresh_type_var = self.fresh_type_var()
        constraints_body = exp.exp_body.accept(self, fresh_type_var)
        return constraints_def | constraints_body | {(type_var, fresh_type_var)}

    def visit_ifThenElse(self, exp, type_var):
        """
        Example:
            >>> e = IfThenElse(Bln(True), Num(42), Num(30))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["('TV_1', 'TV_2')", "(<class 'bool'>, <class 'bool'>)", "(<class 'int'>, 'TV_2')"]
        """
        fresh_type_var_then = self.fresh_type_var()
        constraints_e0 = exp.e0.accept(self, fresh_type_var_then)
        constraints_e1 = exp.e1.accept(self, fresh_type_var_then)
        constraints_cond = exp.cond.accept(self, type(True))
        return constraints_e0 | constraints_e1 | constraints_cond | {(type_var, fresh_type_var_then)}

# End of EvalVisitor class