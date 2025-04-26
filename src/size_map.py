from collections import defaultdict
from .exceptions import *
class SizeMap:
    
    '''Gets the size of the variable from the symtab during semantic phase''' 
    def __init__(self):
        self.size_map = defaultdict(int)
    def add_var(self, var_name: str, size: int):
        self.size_map[var_name] = size
    def modify_size(self, var_name: str, new_size: int):
        self.size_map[var_name] = new_size
    def get_size(self, var: str) -> int:
        if var in self.size_map:
            return self.size_map[var]
        else:
            raise CompileException("Trying to get size for a variable that is not assigned any!!")