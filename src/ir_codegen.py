from .ir import IR
import os
DEFAULT_OUTPUT_DIRECTORY = "generatedIR"

class IRGenerator:
    def __init__(self, irgen):
        self.temp_counter = 0
        self.label_counter = 0
        self.function_labels = {}
        self.output_directory = DEFAULT_OUTPUT_DIRECTORY
        self.outfile = ""
        self.generate = irgen
        if not os.path.exists(self.output_directory):
            os.mkdir(self.output_directory)

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if callable(attr) and self.generate is False:
            return lambda *args, **kwargs: None
        return attr

    def new_temp(self):
        """Generate a new unique temporary variable."""
        temp_var = f'_t{self.temp_counter}'
        self.temp_counter += 1
        return temp_var

    def new_label(self, func_name=None):
        """
        Generate a new unique label. 
        If a function name is provided, use it as the label. (No overloading is supported)
        """
        if func_name:
            if func_name not in self.function_labels:
                self.function_labels[func_name] = f".{func_name}"
            return self.function_labels[func_name]
        
        label = f'_L{self.label_counter}'
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
            for line in ir.code.split('\n'):
                if line[-1] == ':':
                    if line[0] == '.':
                        f.write(line + '\n')
                    else:
                        line = '\t' + line
                        f.write(line + '\n')
                else:
                    line = '\t\t' + line
                    f.write(line + '\n')

    def debug_print(self,ir):
        """
        For printing intermediate values of ir.code
        """
        print("-=====-")
        print(ir.code)
        print("-=====-")

    def join(self,*args):
        ret = ""
        for arg in args:
            if arg == "":
                continue
            ret += arg
            ret += '\n'
        return ret[:-1]

    def identifier(self, ir0, id):
        ir0.place = str(id)

    def constant(self, ir0, const):
        ir0.place = str(const)

    def assignment(self, ir0, ir1, ir2):
        gen = f"{ir1.place} = {ir2.place}"
        ir0.code = self.join(ir2.code, gen)
        self.debug_print(ir0)
    
    def multiple_assignment(self, ir0, ir1, ir2):
        ir0.code = self.join(ir1.code, ir2.code)
        self.debug_print(ir0)

    def op_assign(self, ir0, ir1, ir2, op):
        if op.endswith('='):
            op = op[:-1]
        gen = f"{ir1.place} = {ir1.place} {op} {ir2.place}"
        ir0.code = self.join(ir2.code, gen)
        self.debug_print(ir0)

    def arithmetic_expression(self, ir0, ir1, op, ir2):
        ir0.place = self.new_temp()
        gen = f"{ir0.place} = {ir1.place} {op} {ir2.place}"
        ir0.code = self.join(ir1.code, ir2.code, gen)
        self.debug_print(ir0)

    def inc_dec(self, ir0, ir1, op, post=False):
        gen1 = ""
        if post:
            ir0.place = self.new_temp()
            gen1 = f"{ir0.place} = {ir1.place}"
        else:
            ir0.place = ir1.place
        op = op[0]
        gen2 = f"{ir1.place} = {ir1.place} {op} 1"
        ir0.code = self.join(gen1,gen2)
        self.debug_print(ir0)

    def unary(self, ir0, ir1, op):
        ir0.place = self.new_temp()
        gen = f"{ir0.place} = {op} {ir1.place}"
        ir0.code = self.join(ir1.code,gen)
        self.debug_print(ir0)

    def blockitem(self,ir0,ir1,ir2):
        ir0.code = self.join(ir1.code,ir2.code)
        self.debug_print(ir0)
        
    def translation_unit(self,ir0,ir1,ir2):
        ir0.code = self.join(ir1.code,ir2.code)
        self.debug_print(ir0)

    def function_definition(self,ir0,ir1,ir2,func_name):
        gen1 = self.new_label(func_name) + ':'
        gen2 = "BeginFunc"
        gen3 = "EndFunc"
        ir0.code = self.join(gen1,gen2,ir2.code,gen3)
        self.debug_print(ir0)

    def return_jump(self, ir0,ir1):
        gen = f"return {ir1.place}"
        ir0.code = self.join(ir1.code,gen)

    def argument_expression(self, ir0, ir1, ir2):
        ir0.code = self.join(ir1.code,ir2.code)
        ir0.parameters = ir1.parameters + [ir2.place]
    
    def parameter_init(self, ir0, ir1):
        ir0.parameters = [ir1.place]

    def function_call(self, ir0, ir1, ir2, ret):
        if ir2 is not None:
            # arguments
            if ret == 'void':
                gen1 = ""
                for param  in ir2.parameters:
                    gen1 = self.join(gen1, f"param {param}")
                gen2 = f"call {ir1.place}, {str(len(ir2.parameters))}"
                ir0.code = self.join(ir2.code, gen1, gen2)
            else:
                ir0.place = self.new_temp()
                gen1 = ""
                print(ir2.parameters)
                for param  in ir2.parameters:
                    gen1 = self.join(gen1, f"param {param}")
                gen2 = f"{ir0.place} = call {ir1.place}, {str(len(ir2.parameters))}"
                ir0.code = self.join(ir2.code, gen1, gen2)
        else:
            if ret == 'void':
                ir0.code = "call " + ir1.place
            else:
                ir0.place = self.new_temp()
                gen2 = ir0.place + " = call " + ir1.place + str(len(ir2.parameters))
                ir0.code = self.join(ir2.code, gen2)

    def label_add(self, ir0, label):
        ir0.code = f"{label}:"

    def goto_label(self, ir0, label):
        ir0.code = f"goto {label}"