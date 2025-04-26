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
            return self.handle_two_var_reg(inst.inst[2], inst.inst[5])
        if inst.is_assignment:
            # t1 = t2
            return self.handle_one_var_reg(inst.inst[2])
        return None
    
    def handle_one_var_reg(self, var: str) -> Register:
        """
        Returns single register for the given variable.
        Updates the address descriptor and register descriptor accordingly.
        """
        # check if var is already in reg
        reg = self.add_desc.get_reg_allocated(var)
        if reg:
            print(1)
            return reg[0]
        
        # get free register
        reg = self.reg_desc.get_free_register()
        self.reg_desc.add_var_to_register(reg, var)
        self.add_desc.set_entry_to_reg(var, reg)
        if not reg:
            print(2)
            # need to spill some register
            # TODO
            pass
        return reg
    
    def handle_two_var_reg(self, var1: str, var2: str) -> tuple[Register, Register]:
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
                # TODO
                pass
        
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