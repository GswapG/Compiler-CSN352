from tree import *
from symtab_new import *

class IRGenerator:
    def __init__(self):
        self.temp_counter = 0
        self.label_counter = 0
        self.function_labels = {}

    def new_temp(self):
        """Generate a new unique temporary variable."""
        temp_var = f't{self.temp_counter}'
        self.temp_counter += 1
        return temp_var

    def new_label(self, func_name=None):
        """
        Generate a new unique label. 
        If a function name is provided, use it as the label. (No overloading is supported)
        """
        if func_name:
            if func_name not in self.function_labels:
                self.function_labels[func_name] = func_name
            return self.function_labels[func_name]
        
        label = f'L{self.label_counter}'
        self.label_counter += 1
        return label