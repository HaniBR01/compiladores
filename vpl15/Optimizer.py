from abc import ABC, abstractmethod
from Asm import *
import sys


class Optimizer(ABC):
    """
    This class implements an "Optimization Pass". The pass receives a sequence
    of instructions stored in a program, and produces a new sequence of
    instructions.
    """

    def __init__(self, prog):
        self.prog = prog

    @abstractmethod
    def optimize(self):
        pass


class RegAllocator(Optimizer):
    """This file implements the register allocation pass."""

    def __init__(self, prog):
        # TODO: you might want to save/initialize some stuff in the ctor.
        super().__init__(prog)
        self.var_mapping = {}  # Maps virtual variables to physical registers or memory
        self.physical_registers = ["a0", "a1", "a2", "a3"]
        self.next_memory_offset = 0
        self._analyze_variables()

    def _analyze_variables(self):
        """Analyze all variables used in the program and create mappings using linear scan."""
        # First, identify defined and used variables
        defined_vars, used_vars = self._get_defined_and_used_variables()
        
        # Check for undefined variables
        undefined_vars = used_vars - defined_vars - {"x0", "sp", "ra"}
        if undefined_vars:
            # Print the expected message format and exit
            for var in sorted(undefined_vars):
                print(f"Variavel inexistente {var}")
            sys.exit(1)
        
        # Compute live ranges for defined variables only
        live_ranges = self._compute_live_ranges(defined_vars)
        
        # Sort variables by their start time for linear scan algorithm
        sorted_vars = sorted(live_ranges.items(), key=lambda x: x[1][0])
        
        # Active list keeps track of variables currently using registers
        active = []
        
        for var, (start, end) in sorted_vars:
            # Skip fixed registers
            if var in ["x0", "sp", "ra"]:
                continue
                
            # Expire old intervals - remove variables whose live range has ended BEFORE current start
            active = [(v, s, e, r) for v, s, e, r in active if e > start]
            
            # Try to allocate a register
            if len(active) < len(self.physical_registers):
                # Find available register
                used_regs = {r for v, s, e, r in active}
                available_reg = None
                for reg in self.physical_registers:
                    if reg not in used_regs:
                        available_reg = reg
                        break
                
                if available_reg:
                    self.var_mapping[var] = available_reg
                    active.append((var, start, end, available_reg))
                else:
                    # Spill to memory
                    self.next_memory_offset -= 1
                    self.var_mapping[var] = ("memory", self.next_memory_offset)
            else:
                # Spill to memory
                self.next_memory_offset -= 1
                self.var_mapping[var] = ("memory", self.next_memory_offset)
    
    def _get_defined_and_used_variables(self):
        """Separate variables that are defined vs just used."""
        defined_vars = set()
        used_vars = set()
        
        for inst in self.prog.get_insts():
            # Variables that are defined (destination registers)
            if hasattr(inst, 'rd') and inst.rd:
                defined_vars.add(inst.rd)
            if hasattr(inst, 'reg') and inst.reg and type(inst).__name__ == 'Lw':
                defined_vars.add(inst.reg)
                
            # Variables that are used (source registers)
            if hasattr(inst, 'rs1') and inst.rs1:
                used_vars.add(inst.rs1)
            if hasattr(inst, 'rs2') and inst.rs2:
                used_vars.add(inst.rs2)
            if hasattr(inst, 'base') and inst.base:
                used_vars.add(inst.base)
            if hasattr(inst, 'reg') and inst.reg and type(inst).__name__ == 'Sw':
                used_vars.add(inst.reg)
        
        return defined_vars, used_vars
    
    def _compute_live_ranges(self, defined_vars):
        """Compute live ranges for each variable."""
        live_ranges = {}
        instructions = self.prog.get_insts()
        
        for i, inst in enumerate(instructions):
            variables = self._get_instruction_vars(inst)
            
            # Only compute ranges for defined variables
            for var in variables:
                if var in defined_vars:
                    if var not in live_ranges:
                        live_ranges[var] = [i, i]
                    else:
                        live_ranges[var][1] = i
        
        # Convert to tuple format
        return {var: tuple(range_info) for var, range_info in live_ranges.items()}
    
    def _get_instruction_vars(self, inst):
        """Extract all variable names from an instruction."""
        variables = set()
        
        # Add destination register
        if hasattr(inst, 'rd') and inst.rd:
            variables.add(inst.rd)
        
        # Add source registers
        if hasattr(inst, 'rs1') and inst.rs1:
            variables.add(inst.rs1)
        if hasattr(inst, 'rs2') and inst.rs2:
            variables.add(inst.rs2)
        
        # For store/load instructions
        if hasattr(inst, 'reg') and inst.reg:
            variables.add(inst.reg)
        if hasattr(inst, 'base') and inst.base:
            variables.add(inst.base)
            
        return variables

    def get_val(self, var):
        """
        Informs the value that is associated with the variable var within
        the program prog.
        """
        if var in self.var_mapping:
            mapping = self.var_mapping[var]
            if isinstance(mapping, str):
                # It's a physical register
                return self.prog.get_val(mapping)
            else:
                # It's in memory (mapping is a tuple: ("memory", offset))
                _, offset = mapping
                memory_addr = self.prog.get_val("sp") + offset
                return self.prog.get_mem(memory_addr)
        else:
            # It might be a physical register already
            return self.prog.get_val(var)


    def optimize(self):
        """
        This function perform register allocation. It maps variables into
        memory, and changes instructions, so that they use one of the following
        registers:
        * x0: always the value zero. Can't change.
        * sp: the stack pointer. Starts with the memory size.
        * ra: the return address.
        * a0: function argument 0 (or return address)
        * a1: function argument 1
        * a2: function argument 2
        * a3: function argument 3

        Notice that next to each register we have suggested a usage. You can,
        of course, write on them and use them in other ways. But, at least x0
        and sp you should not overwrite. The first register you can't overwrite,
        actually. And sp is initialized with the number of memory addresses.
        It's good to use it to control the function stack.

        Examples:
        >>> insts = [Addi("a", "x0", 3)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        3

        >>> insts = [Addi("a", "x0", 1), Slti("b", "a", 2)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        1

        >>> insts = [Addi("a", "x0", 3), Slti("b", "a", 2), Xori("c", "b", 5)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        5

        >>> insts = [Addi("sp", "sp", -1),Addi("a", "x0", 7),Sw("sp", 0, "a")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_mem(p.get_val("sp"))
        7

        >>> insts = [Addi("sp", "sp", -1),Addi("a", "x0", 7),Sw("sp", 0, "a")]
        >>> insts += [Lw("sp", 0, "b"), Addi("c", "b", 6)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        13

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Add("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        7

        >>> insts = [Addi("a", "x0", 28),Addi("b", "x0", 4),Div("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        7

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Mul("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        12

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Xor("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        7

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Slt("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        1

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Slt("c", "b", "a")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        0
        
        If you want, you can allocate Jal/Jalr/Beq instructions, but that's not
        necessary for this exercise.

        >>> insts = [Jal("a", 30)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> (p.get_pc(), p.get_val("a1") > 0)
        (30, True)

        >>> insts = [Addi("a", "x0", 30), Jalr("b", "a")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> (p.get_pc(), p.get_val("a1") > 0)
        (30, True)

        >>> insts = [Addi("a", "x0", 3), Addi("b", "a", 0), Beq("a", "b", 30)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_pc()
        30
        """
        new_insts = []
        
        # Initialize stack pointer adjustment if we're using memory
        if self.next_memory_offset < 0:
            # Adjust stack pointer to reserve space for spilled variables
            new_insts.append(Addi("sp", "sp", self.next_memory_offset))
        
        for inst in self.prog.get_insts():
            new_insts.extend(self._transform_instruction(inst))
        
        self.prog.set_insts(new_insts)
    
    def _transform_instruction(self, inst):
        """Transform a single instruction to use physical registers."""
        inst_type = type(inst).__name__
        
        if inst_type == "Addi":
            return self._transform_addi(inst)
        elif inst_type == "Add":
            return self._transform_add(inst)
        elif inst_type == "Sub":
            return self._transform_sub(inst)
        elif inst_type == "Mul":
            return self._transform_mul(inst)
        elif inst_type == "Div":
            return self._transform_div(inst)
        elif inst_type == "Xor":
            return self._transform_xor(inst)
        elif inst_type == "Xori":
            return self._transform_xori(inst)
        elif inst_type == "Slt":
            return self._transform_slt(inst)
        elif inst_type == "Slti":
            return self._transform_slti(inst)
        elif inst_type == "Sw":
            return self._transform_sw(inst)
        elif inst_type == "Lw":
            return self._transform_lw(inst)
        elif inst_type == "Jal":
            return self._transform_jal(inst)
        elif inst_type == "Jalr":
            return self._transform_jalr(inst)
        elif inst_type == "Beq":
            return self._transform_beq(inst)
        else:
            # Return instruction as-is if we don't know how to handle it
            return [inst]
    
    def _get_physical_location(self, var):
        """Get the physical register or generate load/store for memory location."""
        if var in ["x0", "sp", "ra"] or var in self.physical_registers:
            return var
        
        if var in self.var_mapping:
            mapping = self.var_mapping[var]
            if isinstance(mapping, str):
                return mapping  # It's a physical register
            else:
                return None  # It's in memory, needs special handling
        
        return var  # Unknown variable, pass through
    
    def _load_from_memory(self, var, temp_reg):
        """Generate instructions to load a variable from memory to a temporary register."""
        if var not in self.var_mapping:
            return []
        
        mapping = self.var_mapping[var]
        if isinstance(mapping, tuple) and mapping[0] == "memory":
            _, offset = mapping
            return [Lw("sp", offset, temp_reg)]
        
        return []
    
    def _store_to_memory(self, var, temp_reg):
        """Generate instructions to store a temporary register to memory."""
        if var not in self.var_mapping:
            return []
        
        mapping = self.var_mapping[var]
        if isinstance(mapping, tuple) and mapping[0] == "memory":
            _, offset = mapping
            return [Sw("sp", offset, temp_reg)]
        
        return []
    
    def _transform_addi(self, inst):
        rd_phys = self._get_physical_location(inst.rd)
        rs1_phys = self._get_physical_location(inst.rs1)
        
        instructions = []
        
        # Handle source in memory
        if rs1_phys is None:
            instructions.extend(self._load_from_memory(inst.rs1, "ra"))
            rs1_phys = "ra"
        
        # Handle destination in memory
        if rd_phys is None:
            instructions.append(Addi("ra", rs1_phys, inst.imm))
            instructions.extend(self._store_to_memory(inst.rd, "ra"))
        else:
            instructions.append(Addi(rd_phys, rs1_phys, inst.imm))
        
        return instructions
    
    def _transform_add(self, inst):
        rd_phys = self._get_physical_location(inst.rd)
        rs1_phys = self._get_physical_location(inst.rs1)
        rs2_phys = self._get_physical_location(inst.rs2)
        
        instructions = []
        
        # Handle sources in memory
        if rs1_phys is None:
            instructions.extend(self._load_from_memory(inst.rs1, "ra"))
            rs1_phys = "ra"
        
        if rs2_phys is None:
            # If ra is already used, we need another temp register
            temp_reg = "ra" if rs1_phys != "ra" else "a0"
            instructions.extend(self._load_from_memory(inst.rs2, temp_reg))
            rs2_phys = temp_reg
        
        # Handle destination in memory
        if rd_phys is None:
            temp_reg = "ra" if rs1_phys != "ra" and rs2_phys != "ra" else "a0"
            instructions.append(Add(temp_reg, rs1_phys, rs2_phys))
            instructions.extend(self._store_to_memory(inst.rd, temp_reg))
        else:
            instructions.append(Add(rd_phys, rs1_phys, rs2_phys))
        
        return instructions
    
    def _transform_sub(self, inst):
        rd_phys = self._get_physical_location(inst.rd)
        rs1_phys = self._get_physical_location(inst.rs1)
        rs2_phys = self._get_physical_location(inst.rs2)
        
        instructions = []
        
        # Handle sources in memory
        if rs1_phys is None:
            instructions.extend(self._load_from_memory(inst.rs1, "ra"))
            rs1_phys = "ra"
        
        if rs2_phys is None:
            temp_reg = "ra" if rs1_phys != "ra" else "a0"
            instructions.extend(self._load_from_memory(inst.rs2, temp_reg))
            rs2_phys = temp_reg
        
        # Handle destination in memory
        if rd_phys is None:
            temp_reg = "ra" if rs1_phys != "ra" and rs2_phys != "ra" else "a0"
            instructions.append(Sub(temp_reg, rs1_phys, rs2_phys))
            instructions.extend(self._store_to_memory(inst.rd, temp_reg))
        else:
            instructions.append(Sub(rd_phys, rs1_phys, rs2_phys))
        
        return instructions
    
    def _transform_mul(self, inst):
        rd_phys = self._get_physical_location(inst.rd)
        rs1_phys = self._get_physical_location(inst.rs1)
        rs2_phys = self._get_physical_location(inst.rs2)
        
        instructions = []
        
        # Handle sources in memory
        if rs1_phys is None:
            instructions.extend(self._load_from_memory(inst.rs1, "ra"))
            rs1_phys = "ra"
        
        if rs2_phys is None:
            temp_reg = "ra" if rs1_phys != "ra" else "a0"
            instructions.extend(self._load_from_memory(inst.rs2, temp_reg))
            rs2_phys = temp_reg
        
        # Handle destination in memory
        if rd_phys is None:
            temp_reg = "ra" if rs1_phys != "ra" and rs2_phys != "ra" else "a0"
            instructions.append(Mul(temp_reg, rs1_phys, rs2_phys))
            instructions.extend(self._store_to_memory(inst.rd, temp_reg))
        else:
            instructions.append(Mul(rd_phys, rs1_phys, rs2_phys))
        
        return instructions
    
    def _transform_div(self, inst):
        rd_phys = self._get_physical_location(inst.rd)
        rs1_phys = self._get_physical_location(inst.rs1)
        rs2_phys = self._get_physical_location(inst.rs2)
        
        instructions = []
        
        # Handle sources in memory
        if rs1_phys is None:
            instructions.extend(self._load_from_memory(inst.rs1, "ra"))
            rs1_phys = "ra"
        
        if rs2_phys is None:
            temp_reg = "ra" if rs1_phys != "ra" else "a0"
            instructions.extend(self._load_from_memory(inst.rs2, temp_reg))
            rs2_phys = temp_reg
        
        # Handle destination in memory
        if rd_phys is None:
            temp_reg = "ra" if rs1_phys != "ra" and rs2_phys != "ra" else "a0"
            instructions.append(Div(temp_reg, rs1_phys, rs2_phys))
            instructions.extend(self._store_to_memory(inst.rd, temp_reg))
        else:
            instructions.append(Div(rd_phys, rs1_phys, rs2_phys))
        
        return instructions
    
    def _transform_xor(self, inst):
        rd_phys = self._get_physical_location(inst.rd)
        rs1_phys = self._get_physical_location(inst.rs1)
        rs2_phys = self._get_physical_location(inst.rs2)
        
        instructions = []
        
        # Handle sources in memory
        if rs1_phys is None:
            instructions.extend(self._load_from_memory(inst.rs1, "ra"))
            rs1_phys = "ra"
        
        if rs2_phys is None:
            temp_reg = "ra" if rs1_phys != "ra" else "a0"
            instructions.extend(self._load_from_memory(inst.rs2, temp_reg))
            rs2_phys = temp_reg
        
        # Handle destination in memory
        if rd_phys is None:
            temp_reg = "ra" if rs1_phys != "ra" and rs2_phys != "ra" else "a0"
            instructions.append(Xor(temp_reg, rs1_phys, rs2_phys))
            instructions.extend(self._store_to_memory(inst.rd, temp_reg))
        else:
            instructions.append(Xor(rd_phys, rs1_phys, rs2_phys))
        
        return instructions
    
    def _transform_xori(self, inst):
        rd_phys = self._get_physical_location(inst.rd)
        rs1_phys = self._get_physical_location(inst.rs1)
        
        instructions = []
        
        # Handle source in memory
        if rs1_phys is None:
            instructions.extend(self._load_from_memory(inst.rs1, "ra"))
            rs1_phys = "ra"
        
        # Handle destination in memory
        if rd_phys is None:
            instructions.append(Xori("ra", rs1_phys, inst.imm))
            instructions.extend(self._store_to_memory(inst.rd, "ra"))
        else:
            instructions.append(Xori(rd_phys, rs1_phys, inst.imm))
        
        return instructions
    
    def _transform_slt(self, inst):
        rd_phys = self._get_physical_location(inst.rd)
        rs1_phys = self._get_physical_location(inst.rs1)
        rs2_phys = self._get_physical_location(inst.rs2)
        
        instructions = []
        
        # Handle sources in memory
        if rs1_phys is None:
            instructions.extend(self._load_from_memory(inst.rs1, "ra"))
            rs1_phys = "ra"
        
        if rs2_phys is None:
            temp_reg = "ra" if rs1_phys != "ra" else "a0"
            instructions.extend(self._load_from_memory(inst.rs2, temp_reg))
            rs2_phys = temp_reg
        
        # Handle destination in memory
        if rd_phys is None:
            temp_reg = "ra" if rs1_phys != "ra" and rs2_phys != "ra" else "a0"
            instructions.append(Slt(temp_reg, rs1_phys, rs2_phys))
            instructions.extend(self._store_to_memory(inst.rd, temp_reg))
        else:
            instructions.append(Slt(rd_phys, rs1_phys, rs2_phys))
        
        return instructions
    
    def _transform_slti(self, inst):
        rd_phys = self._get_physical_location(inst.rd)
        rs1_phys = self._get_physical_location(inst.rs1)
        
        instructions = []
        
        # Handle source in memory
        if rs1_phys is None:
            instructions.extend(self._load_from_memory(inst.rs1, "ra"))
            rs1_phys = "ra"
        
        # Handle destination in memory
        if rd_phys is None:
            instructions.append(Slti("ra", rs1_phys, inst.imm))
            instructions.extend(self._store_to_memory(inst.rd, "ra"))
        else:
            instructions.append(Slti(rd_phys, rs1_phys, inst.imm))
        
        return instructions
    
    def _transform_sw(self, inst):
        # For Sw instructions, we need to handle both base and reg
        base_phys = self._get_physical_location(inst.base)
        reg_phys = self._get_physical_location(inst.reg)
        
        instructions = []
        
        # Handle base in memory
        if base_phys is None:
            instructions.extend(self._load_from_memory(inst.base, "ra"))
            base_phys = "ra"
        
        # Handle reg in memory
        if reg_phys is None:
            temp_reg = "ra" if base_phys != "ra" else "a0"
            instructions.extend(self._load_from_memory(inst.reg, temp_reg))
            reg_phys = temp_reg
        
        instructions.append(Sw(base_phys, inst.offset, reg_phys))
        return instructions
    
    def _transform_lw(self, inst):
        # For Lw instructions, we need to handle both base and reg
        base_phys = self._get_physical_location(inst.base)
        reg_phys = self._get_physical_location(inst.reg)
        
        instructions = []
        
        # Handle base in memory
        if base_phys is None:
            instructions.extend(self._load_from_memory(inst.base, "ra"))
            base_phys = "ra"
        
        # Handle destination in memory
        if reg_phys is None:
            instructions.append(Lw(base_phys, inst.offset, "ra"))
            instructions.extend(self._store_to_memory(inst.reg, "ra"))
        else:
            instructions.append(Lw(base_phys, inst.offset, reg_phys))
        
        return instructions
    
    def _transform_jal(self, inst):
        rd_phys = self._get_physical_location(inst.rd)
        
        instructions = []
        
        # Handle destination in memory
        if rd_phys is None:
            instructions.append(Jal("ra", inst.imm))
            instructions.extend(self._store_to_memory(inst.rd, "ra"))
        else:
            instructions.append(Jal(rd_phys, inst.imm))
        
        return instructions
    
    def _transform_jalr(self, inst):
        rd_phys = self._get_physical_location(inst.rd)
        rs1_phys = self._get_physical_location(inst.rs1)
        
        instructions = []
        
        # Handle source in memory
        if rs1_phys is None:
            instructions.extend(self._load_from_memory(inst.rs1, "ra"))
            rs1_phys = "ra"
        
        # Handle destination in memory
        if rd_phys is None:
            temp_reg = "ra" if rs1_phys != "ra" else "a0"
            instructions.append(Jalr(temp_reg, rs1_phys, inst.offset))
            instructions.extend(self._store_to_memory(inst.rd, temp_reg))
        else:
            instructions.append(Jalr(rd_phys, rs1_phys, inst.offset))
        
        return instructions
    
    def _transform_beq(self, inst):
        rs1_phys = self._get_physical_location(inst.rs1)
        rs2_phys = self._get_physical_location(inst.rs2)
        
        instructions = []
        
        # Handle sources in memory
        if rs1_phys is None:
            instructions.extend(self._load_from_memory(inst.rs1, "ra"))
            rs1_phys = "ra"
        
        if rs2_phys is None:
            temp_reg = "ra" if rs1_phys != "ra" else "a0"
            instructions.extend(self._load_from_memory(inst.rs2, temp_reg))
            rs2_phys = temp_reg
        
        instructions.append(Beq(rs1_phys, rs2_phys, inst.imm))
        return instructions