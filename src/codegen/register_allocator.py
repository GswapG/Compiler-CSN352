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
    
    def get_register(self, inst: "Instruction") -> tuple[Register]:
        """
        Parse the inst (tac) to find what variables need registers.
        Returns a list of registers (memory locations)
        """
        ret = []

        if inst.is_param:
            param = inst.inst[1]
            return self.handle_param(param)

        if inst.is_addr:
            t1 = inst.inst[0]
            r1 = self.get_lhs_register_for_assignment(t1)
            return r1 + (None,)

        if inst.is_relop:  # Add this case first
        # t1 = t2 (type) relop t3
            t1 = inst.inst[0]
            t2 = inst.inst[2]
            t3 = inst.inst[5]
            size = self.code_generator.get_size_idx(inst.inst[3][1:-1])
            r1 = self.get_lhs_register_for_assignment(t1)
            return r1 + (None,)

        if inst.is_operation:
            # t1 = t2 op t3
            t3 = inst.inst[5]
            ret = None
            if self.code_generator.is_constant(t3):
                ret = self.handle_one_var_reg(inst.inst[2], self.code_generator.get_size_idx(inst.inst[3][1:-1]))
            elif self.code_generator.is_constant(t3):
                ret = self.handle_one_var_reg(inst.inst[5], self.code_generator.get_size_idx(inst.inst[3][1:-1]))
            else:
                ret = self.handle_two_var_reg(inst.inst[2], inst.inst[5], self.code_generator.get_size_idx(inst.inst[3][1:-1]))
            # need to remove register for lhs from all other add desc
            for y in self.reg_desc.get_register_values(ret[0]):
                if y == inst.inst[2]:
                    continue
                self.add_desc.discard_reg_for_var(y,ret[0])
            self.reg_desc.set_register_values(ret[0], inst.inst[0])
            self.add_desc.set_entry_to_reg(inst.inst[0],ret[0])
            return ret
        
        if inst.is_assignment:
            # t1 = t2
            t1 = inst.inst[0]
            t2 = inst.inst[2]
            if self.code_generator.is_constant(t2):
                # this is only called in the case of temp = const
                return self.get_lhs_register_for_assignment(t1)
            if t1[0] == '@':
                # t1 is temp
                reg1 = self.get_lhs_register_for_assignment(t1) 
                return reg1 + self.get_rhs_register_for_assignment(t2, reg1)
            else:
                # t1 is named
                return self.get_rhs_register_for_assignment(t2)
        return None
    
    def handle_param(self, param):
        # if allocated, return reg
        reg = self.add_desc.get_reg_allocated(param)
        if reg:
            return reg[0]
        else:
            return None
        # else return None

    def get_lhs_register_for_assignment(self, var: str) -> tuple[Register]:
        reg = self.add_desc.get_reg_allocated(var)
        if reg is not None:
            return (reg[0],)
        # get free register
        reg = self.reg_desc.get_free_register()
        if reg is None:
            # need to spill some register
            # TODO : spill and get reg
            pass
        self.reg_desc.set_register_values(reg, var)
        self.add_desc.set_entry_to_reg(var, reg)
        return (reg,)
    
    def get_lhs_register_for_assignment2(self, var: str,ptr_reg: Register) -> tuple[Register]:
        reg = self.add_desc.get_reg_allocated(var)
        if reg is not None:
            return (reg[0],)
        # get free register
        reg = self.reg_desc.get_free_register()
        # gen11 = f"lea {reg[0]}, [{ptr_reg}]"
        # self.code_generator.emit(gen11)
        if reg is None:
            # need to spill some register
            # TODO : spill and get reg
            pass
        self.reg_desc.set_register_values(reg, var)
        self.add_desc.set_entry_to_reg(var, reg)
        return (reg,)


    def get_reg_for_deref(self, ptr_var: str) -> tuple[Register]:
        """
        Get register for pointer dereferencing operations (*t1 = t2).
        Allocates a new register and loads the memory value of the pointer into it.
        
        Args:
            ptr_var: The pointer variable (without the * operator)
        Returns:
            tuple containing the allocated register
        """
        # First check if ptr_var already has an allocated register
        reg = self.add_desc.get_reg_allocated(ptr_var)
        if reg is not None:
            return (reg[0],)

        # Get a free register for the pointer
        reg = self.reg_desc.get_free_register()
        if reg is None:
            # TODO: implement spilling if no free register
            pass

        # Load the address/value from ptr_var into the register
        size = self.code_generator.get_size_idx(size=self.code_generator.size_map.get_size(ptr_var))
        address = self.code_generator.address_map.get_address(ptr_var)
        
        # Load the value of ptr_var into the register
        self.code_generator.emit(f'mov {reg[size]}, {self.code_generator.size_specifiers[size]} [rbp{address}]')
        
        # Update register descriptors
        self.reg_desc.set_register_values(reg, ptr_var)
        self.add_desc.set_entry_to_reg(ptr_var, reg)

        return (reg,)


    def get_rhs_register_for_assignment(self, var: str, reg_to_not_spill = None) -> tuple[Register]:
        regs = self.add_desc.get_reg_allocated(var)
        if regs is not None:
            return (regs[0],)
        # get free register
        reg = self.reg_desc.get_free_register()
        if reg is None:
            # need to spill some register
            # TODO : spill and get reg
            pass 
        print(var)  
        size = self.code_generator.get_size_idx(size=self.code_generator.size_map.get_size(var))
        code = f'mov {reg[size]}, {self.code_generator.size_specifiers[size]} [rbp{self.code_generator.address_map.get_address(var)}]'
        self.code_generator.emit(code)
        self.reg_desc.set_register_values(reg, var)
        self.add_desc.add_reg_to_entry(var, reg)
        return (reg,)


    def handle_one_var_reg(self, var: str, size = 0) -> tuple[Register]:
        """
        Returns single register for the given variable.
        Updates the address descriptor and register descriptor accordingly.
        """
        # check if var is already in reg
        reg = self.add_desc.get_reg_allocated(var)
        if reg:
            self.add_desc.discard_reg_for_var(var, reg[0])
            return (reg[0],)
        
        # get free register
        reg = self.reg_desc.get_free_register()
        if not reg:
            # need to spill some register
            # TODO: spill and get reg
            pass

        self.reg_desc.add_var_to_register(reg, var)
        
        # Check if var is a constant before trying to load from memory
        if self.code_generator.is_constant(var):
            self.code_generator.emit(f'mov {reg[size]}, {var}')
        else:
            # emit code for loading register from memory
            address = self.code_generator.address_map.get_address(var)
            code = f'mov {reg[size]}, {self.code_generator.size_specifiers[size]} [rbp{address}]'
            self.code_generator.emit(code)
        
        return (reg,)
    
    def handle_two_var_reg(self, var1: str, var2: str, size = 0) -> tuple[Register, Register]:
        """
        Returns two registers for the given variables.
        Updates the address descriptor and register descriptor accordingly.
        """
        # Handle var1
        reg1 = self.add_desc.get_reg_allocated(var1)
        if reg1:
            reg1 = reg1[0]
        else:
            reg1 = self.reg_desc.get_free_register()
            if not reg1:
                # TODO: spill and get reg1
                pass
            # Check if var1 is a constant
            if self.code_generator.is_constant(var1):
                self.code_generator.emit(f'mov {reg1[size]}, {var1}')
            else:
                print("asdasda12")
                print(self.code_generator.address_map)
                address = self.code_generator.address_map.get_address(var1)
                self.code_generator.emit(f'mov {reg1[size]}, {self.code_generator.size_specifiers[size]} [rbp{address}]')

        # Handle var2
        reg2 = self.add_desc.get_reg_allocated(var2)
        if reg2:
            reg2 = reg2[0]
        else:
            reg2 = self.reg_desc.get_free_register()
            if not reg2:
                # TODO: spill and get reg2
                pass
            # Check if var2 is a constant
            if self.code_generator.is_constant(var2):
                self.code_generator.emit(f'mov {reg2[size]}, {var2}')
            else:
                address = self.code_generator.address_map.get_address(var2)
                self.code_generator.emit(f'mov {reg2[size]}, {self.code_generator.size_specifiers[size]} [rbp{address}]')

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

    def push_caller_saved(self):
        """
        Called before function call.
        Any caller saved register in use will be stored onto the stack.
        """
        for reg in self.reg_desc.registers:
            if reg.caller_saved:
                # push to stack
                self.regs_on_stack.append(reg)
                code = f'push {reg[0]}'
                self.code_generator.emit(code)
        # 9 registers must have been pushed to stack
        # need to sub rsp 8
        code = f'sub rsp, 8'
        self.code_generator.emit(code)
    
    def pop_caller_saved(self):
        """
        Called after function call to restore state of caller saved registers.
        """
        code = f'add rsp, 8'
        self.code_generator.emit(code)
        for reg in reversed(self.regs_on_stack):
            code = f'pop {reg[0]}'
            self.code_generator.emit(code)
        self.regs_on_stack = []
