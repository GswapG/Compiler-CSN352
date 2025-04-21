from .add_desc import *
from .reg_desc import *
from .codegenerator import *

class RegisterAllocator:
    """
    Takes in entire tac instruction 
    Gives out available registers for operands
    Updates Register and Address Descriptors
    """
    def __init___(self, registers: list[Register], code_generator: CodeGenerator):
        """
        Create address and register descriptor
        """
        self.add_desc = AddressDescriptor()
        self.reg_desc = RegisterDescriptor(registers)
        self.code_generator = code_generator

    def get_register(self,inst: str):
        """
        Parse the inst (tac) to find what variables need registers.
        Returns a list of registers (memory locations)
        """
        pass
    
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

