import sys
from abc import ABC, abstractmethod
from Expression import *
import Asm as AsmModule


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
    

class RenameVisitor(Visitor):
    """
    This visitor traverses the AST of a program, renaming variables to ensure
    that they all have different names.

    Usage:
        >>> e0 = Let('x', Num(2), Add(Var('x'), Num(3)))
        >>> e1 = Let('x', e0, Mul(Var('x'), Num(10)))
        >>> e0.identifier == e1.identifier
        True

        >>> e0 = Let('x', Num(2), Add(Var('x'), Num(3)))
        >>> e1 = Let('x', e0, Mul(Var('x'), Num(10)))
        >>> r = RenameVisitor()
        >>> e1.accept(r, {})
        >>> e0.identifier == e1.identifier
        False

        >>> x0 = Var('x')
        >>> x1 = Var('x')
        >>> e0 = Let('x', Num(2), Add(x0, Num(3)))
        >>> e1 = Let('x', e0, Mul(x1, Num(10)))
        >>> x0.identifier == x1.identifier
        True

        >>> x0 = Var('x')
        >>> x1 = Var('x')
        >>> e0 = Let('x', Num(2), Add(x0, Num(3)))
        >>> e1 = Let('x', e0, Mul(x1, Num(10)))
        >>> r = RenameVisitor()
        >>> e1.accept(r, {})
        >>> x0.identifier == x1.identifier
        False
    """
    
    def __init__(self):
        self.counter = 0
    
    def next_name(self, base_name):
        self.counter += 1
        return f"{base_name}_{self.counter}"
    
    def visit_var(self, exp, arg):
        if exp.identifier in arg:
            exp.identifier = arg[exp.identifier]

    def visit_bln(self, exp, arg):
        pass

    def visit_num(self, exp, arg):
        pass

    def visit_eql(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_add(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_sub(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_mul(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_div(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_leq(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_lth(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_neg(self, exp, arg):
        exp.exp.accept(self, arg)

    def visit_not(self, exp, arg):
        exp.exp.accept(self, arg)

    def visit_let(self, exp, arg):
        # First, process the definition expression with current environment
        exp.exp_def.accept(self, arg)
        
        # Create a new name for this let binding
        old_identifier = exp.identifier
        new_identifier = self.next_name(old_identifier)
        exp.identifier = new_identifier
        
        # Create a new environment for the body
        new_arg = arg.copy()
        new_arg[old_identifier] = new_identifier
        
        # Process the body with the new environment
        exp.exp_body.accept(self, new_arg)


class GenVisitor(Visitor):
    """
    The GenVisitor class compiles arithmetic expressions into a low-level
    language.
    """

    def __init__(self):
        self.next_var_counter = 0

    def next_var_name(self):
        self.next_var_counter += 1
        return f"v{self.next_var_counter}"

    def visit_var(self, exp, prog):
        """
        Usage:
            >>> e = Var('x')
            >>> p = AsmModule.Program(1000, {"x":1}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            1
        """
        return exp.identifier

    def visit_bln(self, exp, env):
        """
        Usage:
            >>> e = Bln(True)
            >>> p = AsmModule.Program(1000, {}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            1

            >>> e = Bln(False)
            >>> p = AsmModule.Program(1000, {}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            0
        """
        if exp.bln:
            p = env
            var_name = self.next_var_name()
            p.add_inst(AsmModule.Addi(var_name, "x0", 1))
            return var_name
        else:
            return "x0"

    def visit_num(self, exp, prog):
        """
        Usage:
            >>> e = Num(13)
            >>> p = AsmModule.Program(1000, {}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            13
        """
        p = prog
        var_name = self.next_var_name()
        p.add_inst(AsmModule.Addi(var_name, "x0", exp.num))
        return var_name

    def visit_eql(self, exp, prog):
        """
        >>> e = Eql(Num(13), Num(13))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Eql(Num(13), Num(10))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Eql(Num(-1), Num(1))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0
        """
        left_reg = exp.left.accept(self, prog)
        right_reg = exp.right.accept(self, prog)
        result_reg = self.next_var_name()
        sub_reg = self.next_var_name()
        msub_reg = self.next_var_name()
        
        prog.add_inst(AsmModule.Sub(sub_reg, left_reg, right_reg))
        prog.add_inst(AsmModule.Slti(sub_reg, sub_reg, 1))

        prog.add_inst(AsmModule.Sub(msub_reg, right_reg, left_reg))
        prog.add_inst(AsmModule.Slti(msub_reg, msub_reg, 1))

        prog.add_inst(AsmModule.Mul(result_reg, sub_reg, msub_reg))
        return result_reg

    def visit_add(self, exp, prog):
        """
        >>> e = Add(Num(13), Num(-13))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Add(Num(13), Num(10))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        23
        """
        left_reg = exp.left.accept(self, prog)
        right_reg = exp.right.accept(self, prog)
        result_reg = self.next_var_name()
        prog.add_inst(AsmModule.Add(result_reg, left_reg, right_reg))
        return result_reg

    def visit_sub(self, exp, prog):
        """
        >>> e = Sub(Num(13), Num(-13))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        26

        >>> e = Sub(Num(13), Num(10))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        3
        """
        left_reg = exp.left.accept(self, prog)
        right_reg = exp.right.accept(self, prog)
        result_reg = self.next_var_name()
        prog.add_inst(AsmModule.Sub(result_reg, left_reg, right_reg))
        return result_reg

    def visit_mul(self, exp, prog):
        """
        >>> e = Mul(Num(13), Num(2))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        26

        >>> e = Mul(Num(13), Num(10))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        130
        """
        left_reg = exp.left.accept(self, prog)
        right_reg = exp.right.accept(self, prog)
        result_reg = self.next_var_name()
        prog.add_inst(AsmModule.Mul(result_reg, left_reg, right_reg))
        return result_reg

    def visit_div(self, exp, prog):
        """
        >>> e = Div(Num(13), Num(2))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        6

        >>> e = Div(Num(13), Num(10))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1
        """
        left_reg = exp.left.accept(self, prog)
        right_reg = exp.right.accept(self, prog)
        result_reg = self.next_var_name()
        prog.add_inst(AsmModule.Div(result_reg, left_reg, right_reg))
        return result_reg

    def visit_leq(self, exp, prog):
        """
        >>> e = Leq(Num(3), Num(2))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Leq(Num(3), Num(3))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Leq(Num(2), Num(3))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Leq(Num(-3), Num(-2))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Leq(Num(-3), Num(-3))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Leq(Num(-2), Num(-3))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0
        """
        left_reg = exp.left.accept(self, prog)
        right_reg = exp.right.accept(self, prog)
        result_reg = self.next_var_name()
        sub_reg = self.next_var_name()
        prog.add_inst(AsmModule.Sub(sub_reg, left_reg, right_reg))
        prog.add_inst(AsmModule.Slti(result_reg, sub_reg, 1))
        return result_reg

    def visit_lth(self, exp, prog):
        """
        >>> e = Lth(Num(3), Num(2))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Lth(Num(3), Num(3))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Lth(Num(2), Num(3))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1
        """
        left_reg = exp.left.accept(self, prog)
        right_reg = exp.right.accept(self, prog)
        result_reg = self.next_var_name()
        prog.add_inst(AsmModule.Slt(result_reg, left_reg, right_reg))
        return result_reg

    def visit_neg(self, exp, prog):
        """
        >>> e = Neg(Num(3))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        -3

        >>> e = Neg(Num(0))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Neg(Num(-3))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        3
        """
        exp_reg = exp.exp.accept(self, prog)
        result_reg = self.next_var_name()
        prog.add_inst(AsmModule.Sub(result_reg, "x0", exp_reg))
        return result_reg

    def visit_not(self, exp, prog):
        """
        >>> e = Not(Bln(True))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Not(Bln(False))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Not(Num(0))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Not(Num(-2))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Not(Num(2))
        >>> p = AsmModule.Program(1000, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0
        """
        exp_reg = exp.exp.accept(self, prog)
        result_reg = self.next_var_name()
        temp1_reg = self.next_var_name()
        temp2_reg = self.next_var_name()

        prog.add_inst(AsmModule.Slti(temp1_reg, exp_reg, 1))

        prog.add_inst(AsmModule.Sub(exp_reg, "x0", exp_reg))
        prog.add_inst(AsmModule.Slti(temp2_reg, exp_reg, 1))

        prog.add_inst(AsmModule.Mul(result_reg, temp1_reg, temp2_reg))
        return result_reg

    def visit_let(self, exp, prog):
        """
        Usage:
            >>> e = Let('v', Not(Bln(False)), Var('v'))
            >>> p = AsmModule.Program(1000, {}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            1

            >>> e = Let('v', Num(2), Add(Var('v'), Num(3)))
            >>> p = AsmModule.Program(1000, {}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            5

            >>> e0 = Let('x', Num(2), Add(Var('x'), Num(3)))
            >>> e1 = Let('y', e0, Mul(Var('y'), Num(10)))
            >>> p = AsmModule.Program(1000, {}, [])
            >>> g = GenVisitor()
            >>> v = e1.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            50
        """
        d_name = exp.exp_def.accept(self, prog)
        prog.add_inst(AsmModule.Addi(exp.identifier, d_name, 0))
        v_name = exp.exp_body.accept(self, prog)
        return v_name