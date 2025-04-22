from collections import defaultdict
from .exceptions import *
## ADDED THIS TO MAP VARIABLES TO MEMORY LOCATIONS 
## MADE SEPARATE DATA STRUCTURE SO SYMBOL TABLE NEED NOT BE PASSED TO CODEGEN
## FOR NAMED VARIABLES, ADDRESSES WILL BE ASSIGNED AT/BEFORE SEMANTIC PHASE
## MODIFICATIONS CAN BE MADE DURING CODEGEN FOR TEMP VARS AS WELL AS FOR VARIABLE LENGTH ARRAYS

class AddressMap:
    """
    Maps variables (temp and named) to memory locations on stack
    """
    def __init__(self):
        self.map = defaultdict(int) # str -> int
    
    def add_var(self, var_name: str, address: int):
        self.map[var_name] = address

    def modify_address(self, var_name: str, new_address: int):
        self.map[var_name] = new_address

    def get_address(self, var: str) -> int:
        if var in self.map:
            return self.map[var]
        else:
            raise CompileException("Trying to get address for a variable that is not assigned any!!")