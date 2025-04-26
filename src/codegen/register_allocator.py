from .add_desc import *
from .reg_desc import *
from .codegenerator import *

class RegisterAllocator:
    """
    Takes in entire tac instruction 
    Gives out available registers for operands
    Updates Register and Address Descriptors
    """
    def __init__(self, registers: list[Register], code_generator: "CodeGenerator"):
        """
        Create address and register descriptor
        """
        self.add_desc = AddressDescriptor()
        self.reg_desc = RegisterDescriptor(registers)
        self.code_generator = code_generator
        self.regs_on_stack = [] #list of caller saved registers stored on stack (before function call)

    def clear_register_entry(self, var: str):
        pass

    def remove_registers(self, var: str):
        self.add_desc.remove_registers(var)

    def set_next_use(self, use: defaultdict):
        self.next_use = use
    
    def get_register(self, inst: "Instruction") -> list[Register]:
        """
        Parse the inst (tac) to find what variables need registers.
        Returns a list of registers (memory locations)
        """
        ret = []
        
        if inst.is_operation:
            # t1 = t2 op t3
            t3 = inst.inst[5]
            ret = None
            if self.code_generator.is_constant(t3):
                ret = self.handle_one_var_reg(inst.inst[2], self.code_generator.get_size_idx(inst.inst[3][1:-1]))
            else:
                ret = self.handle_two_var_reg(inst.inst[2], inst.inst[5], self.code_generator.get_size_idx(inst.inst[3][1:-1]))
            self.reg_desc.set_register_values(ret[0], inst.inst[0])
            self.add_desc.set_entry_to_reg(inst.inst[0],ret[0])
            return ret
        if inst.is_assignment:
            # t1 = t2
            t1 = inst.inst[0]
            t2 = inst.inst[2]
            if self.code_generator.is_constant(t2):
                return self.handle_one_var_reg(t1, self.code_generator.get_size_idx(inst.inst[3][1:-1]))
            if t1[0] == '@':
                # t1 is temp
                if t2[0] == '@':
                    # t2 is temp
                    pass
                else:
                    # t2 is named
                    pass
            else:
                # t1 is named
                if t2[0] == '@':
                    return self.get_rhs_register_for_assignment(t2)
                else:
                    # t2 is named
                    pass
        return None
    
    def get_lhs_register_for_assignment(self, var: str) -> tuple[Register]:
        pass

    def get_rhs_register_for_assignment(self, var: str) -> tuple[Register]:
        reg = self.add_desc.get_reg_allocated(var)
        if reg is not None:
            return (reg[0],)
        return None

    def handle_one_var_reg(self, var: str,size = 0) -> tuple[Register]:
        """
        Returns single register for the given variable.
        Updates the address descriptor and register descriptor accordingly.
        """
        # check if var is already in reg
        reg = self.add_desc.get_reg_allocated(var)
        print(reg)
        if reg:
            print(reg[0])
            self.add_desc.discard_reg_for_var(var, reg[0])
            print(reg)
            return (reg[0],)
        
        # get free register
        reg = self.reg_desc.get_free_register()
        self.reg_desc.add_var_to_register(reg, var)
        self.add_desc.set_entry_to_reg(var, reg)
        # emit code for loading register
        address = self.code_generator.address_map.get_address(var)
        code = f'mov {self.code_generator.size_specifiers[size]} {reg[size]}, [rbp{address}]'
        self.code_generator.emit(code)
        if not reg:
            print(2)
            # need to spill some register
            # TODO
            pass
        return (reg,)
    
    def handle_two_var_reg(self, var1: str, var2: str, size = 0) -> tuple[Register, Register]:
        """
        Returns two registers for the given variables.
        Updates the address descriptor and register descriptor accordingly.
        """
        # check if var1 is already in reg
        reg1 = self.add_desc.get_reg_allocated(var1)
        if reg1:
            reg1 = reg1[0]
        else:
            # get free register
            reg1 = self.reg_desc.get_free_register()
            if not reg1:
                # need to spill some register
                # TODO : spill and get reg1
                pass
            # emit code for loading var1 to reg1
            address = self.code_generator.address_map.get_address(var1)
            code = f'mov {self.code_generator.size_specifiers[size]} {reg1[size]}, [rbp{address}]'
            self.code_generator.emit(code)
        # check if var2 is already in reg
        reg2 = self.add_desc.get_reg_allocated(var2)
        if reg2:
            reg2 = reg2[0]
        else:
            # get free register
            reg2 = self.reg_desc.get_free_register()
            if not reg2:
                # need to spill some register
                # make sure not to spill reg1
                # TODO
                pass
            # emit code for loading var2 to reg2
            address = self.code_generator.address_map.get_address(var2)
            code = f'mov {self.code_generator.size_specifiers[size]} {reg2[size]}, [rbp{address}]'
            self.code_generator.emit(code)
        return (reg1, reg2)

    def spill_selector(self,uses: defaultdict):
        """
        Selects register to spill based on heuristic (least uses)
        Spills the selected register
        Emits required instructions using self.code_generator
        Returns the selected register
        """
        pass

    def spill(self, var: str) -> Register:
        """
        Spills register corresponding to given var.
        Updates descriptors accordingly
        """
        regs = self.add_desc.get_reg_allocated(var)
        if regs is None:
            raise CompileException(f"No register contains var, yet an attempt was made to spill it")
        
        reg = regs[0]
        self.reg_desc.clear_register(reg)
        self.add_desc.discard_reg_for_var(var, reg)
        return reg
    
    def store_all(self):
        """
        To be called at the end of a block to store all variables in memory and free all registers.
        """
        pass

    def push_regs_to_stack(self):
        """
        Called before function call.
        Any caller saved register in use will be stored onto the stack.
        """
        pass
    
    def pop_regs_from_stack(self):
        """
        Called after function call to restore state of caller saved registers.
        """
        pass
