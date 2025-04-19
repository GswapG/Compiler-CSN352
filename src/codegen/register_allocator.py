from .add_desc import *
from .reg_desc import *

class RegisterAllocator:
    """
    Takes in entire tac instruction 
    Gives out available registers for operands
    Updates Register and Address Descriptors
    """
    def __init___(self):
        """
        Create address and register descriptor
        """
        self.add_desc = AddressDescriptor()
        self.reg_desc = RegisterDescriptor()

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
        Returns the selected register
        """
        pass

    def spill(self, var: str):
        """
        Spills register corresponding to given var.
        Updates descriptors accordingly
        """
        regs = self.add_desc.get_reg_allocated(var)
        if regs is None:
            raise CompileException(f"No register contains var, yet an attempt was made to spill it")
        
        reg = regs[0]
        self.reg_desc.clear(reg)
        
