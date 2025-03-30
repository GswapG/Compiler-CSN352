from .ir import IR
import os
DEFAULT_OUTPUT_DIRECTORY = "generatedIR"

class IRGenerator:
    def __init__(self):
        self.temp_counter = 0
        self.label_counter = 0
        self.function_labels = {}
        self.output_directory = DEFAULT_OUTPUT_DIRECTORY
        self.outfile = ""
        if not os.path.exists(self.output_directory):
            os.mkdir(self.output_directory)

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
    
    def set_out_directory(self, dir):
        """
        Set path for IR output (directory)
        """
        if not os.path.exists(dir):
            os.mkdir(dir)
        self.output_directory = dir

    def set_out_file(self, out):
        """
        Set name of output file (only filename, path comes from output directory)
        """
        out = os.path.splitext(out)[0]
        out += '.tac'
        self.outfile = out

    def print_final_code(self, ir):
        """
        Pushes final IR to outfile
        """
        filepath = os.path.join(self.output_directory,self.outfile)
        with open(filepath, "w") as f:
            f.write(ir.code)
