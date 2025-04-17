from collections import defaultdict
from ..exceptions import *
## MAYBE UPDATE LIST OF REGISTERS TO SET
## MAYBE ADD A REGISTER CLASS
class AddressDescriptor:
    def __init__(self):
        """
        self.address is list[list of registers, list (haaving single value if in mem, otherwsie empty)]
        mem is stored as offset to rbp
        register: string
        mem: None or int
        """
        self.address = defaultdict(list)
    
    def create_entry(self, var):
        if not var in self.address.keys():
            self.address[var] = [[],None]
    
    def add_reg_to_entry(self, var, reg):
        """
        Appends new reg to existing (no clear)
        """
        if self.address.get(var):
            if reg not in self.address.get(var)[0]: ## REDUNDANT CHECK??
                self.address[var][0].append(reg)
        else:
            raise CompileException(f"Variable {var} does not exist in Address Descriptor")

    def set_entry_to_reg(self, var, reg):
        """
        Clears register entries and sets mem to None
        Sets reg as only location
        """ 
        if self.address.get(var):
            self.address[var] = [[reg],None]
        else:
            raise CompileException(f"Variable {var} does not exist in Address Descriptor")

    def get_mem_location(self, var:str):
        """
        Returns memory location (if stored)
        Otherwise returns None
        """
        temp = self.address.get(var)
        if temp:
            if temp[1]:
                return temp[1][0]
            else: 
                return None
        else:
            raise CompileException(f"Variable {var} does not exist in Address Descriptor")

    def in_mem(self, var:str):
        """
        Returns true if in mem
        False otherwise
        """
        temp = self.address.get(var)
        if temp:
            if temp[1]:
                return True
            else: 
                return False
            
        else:
            raise CompileException(f"Variable {var} does not exist in Address Descriptor")

    def get_reg_allocated(self,var:str) -> list | None:
        """
        Returns list of allocated registers.
        Returns None otherwise
        """
        temp = self.address.get(var)
        if temp:
            if temp[0]:
                return temp[0]
            else:
                return None
        else:
            raise CompileException(f"Variable {var} does not exist in Address Descriptor")


