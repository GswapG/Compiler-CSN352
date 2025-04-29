from .ir import IR
import os
import copy
from .exceptions import *
from .utils import get_size_from_type
from .compatible import dominating_type
from .type_map import TypeMap
DEFAULT_OUTPUT_DIRECTORY = "generatedIR"

class IRGenerator:
    def __init__(self, irgen):
        self.temp_counter = 0
        self.label_counter = 0
        self.bp_counter = 0
        self.function_labels = {}
        self.output_directory = DEFAULT_OUTPUT_DIRECTORY
        self.outfile = ""
        self.generate = irgen
        self.type_map = TypeMap()
        if not os.path.exists(self.output_directory):
            os.mkdir(self.output_directory)

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if callable(attr) and self.generate is False:
            return lambda *args, **kwargs: None
        return attr

    def new_temp(self,dtype=None):
        """Generate a new unique temporary variable."""
        temp_var = f'@t{self.temp_counter}'
        self.temp_counter += 1
        self.type_map.set_var(temp_var,dtype)
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
        
        label = f'$L{self.label_counter}'
        self.label_counter += 1
        return label
    
    def bp_label(self, func_name=None):
        """
        Generate a new unique label. 
        If a function name is provided, use it as the label. (No overloading is supported)
        """
        if func_name:
            if func_name not in self.function_labels:
                self.function_labels[func_name] = f".{func_name}"
            return self.function_labels[func_name]
        
        label = f'$BP{self.bp_counter}'
        self.bp_counter += 1
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
        if ir.code == "":
            return None
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
        return filepath

    def debug_print(self,ir):
        """
        For printing intermediate values of ir.code
        """
        # print("-=====-")
        # print(ir.code)
        # print("-=====-")
        pass

    def join(self,*args):
        """
        Joins strings with newlines in between
        """
        ret = ""
        for arg in args:
            if arg == "":
                continue
            ret += arg
            ret += '\n'
        return ret[:-1]
    
    def remove_lastline(self,ir):
        """
        Remove the last line
        """
        index = ir.code.rfind("\n")
        if index != -1:
            ir.code = ir.code[:index]
        return ir.code

    def dom_type(self, ir1_data_type, ir2_data_type):
        return ir1_data_type if dominating_type(ir1_data_type, ir2_data_type) else ir2_data_type
    
    def convert(self,t1,t2):
        print(t1,t2)
        t1 = t1.replace(' ', '_')
        t2 = t2.replace(' ', '_')
        print(t1,t2)
        cvt = f"{t1}To{t2}"
        return cvt
    
    # Functions for actual IR rules
    def identifier(self, ir0, id):
        ir0.place = str(id)

    def declarator_pointer(self, ir0, id):
        ir0.place = str(id)

    def constant(self, ir0, const):
        ir0.place = str(const)

    def string(self, ir0, const):
        ir0.place = str(const.encode('unicode_escape').decode('utf-8'))

    def assignment(self, ir0, ir1, ir2):
        if ir2.bpneed>0:
            self.resolve_exp(ir2)
        gen = f"{ir1.place} = {ir2.place}"
        if ir1.data_type != ir2.data_type:
            cvt = self.convert(ir2.data_type,ir1.data_type)
            gen =  f"{ir1.place} = {cvt} {ir2.place}"
        ir0.code = self.join(ir1.code, ir2.code, gen)
        ir0.place = ir1.place
        self.debug_print(ir0)
    
    def multiple_assignment(self, ir0, ir1, ir2):
        ir0.code = self.join(ir1.code, ir2.code)
        self.debug_print(ir0)

    def op_assign(self, ir0, ir1, ir2, op):
        dom_type = self.dom_type(ir1.data_type,ir2.data_type).replace(' ','_')
        gen1 = ""
        if ir1.data_type.replace(' ','_') != dom_type:
            cvt = self.convert(ir1.data_type,dom_type)
            new_temp = self.new_temp(dom_type)
            gen1 = f"{new_temp} = {cvt} {ir1.place}"
            ir1.place = new_temp
        if ir2.data_type.replace(' ','_') != dom_type:
            cvt = self.convert(ir1.data_type,dom_type)
            new_temp = self.new_temp(dom_type)
            gen1 = f"{new_temp} = {cvt} {ir2.place}"
            ir2.place = new_temp
        if op.endswith('='):
            op = op[:-1]
        op = f"({dom_type}) {op}"
        gen2 = f"{ir1.place} = {ir1.place} {op} {ir2.place}"
        gen3 = ""
        if gen1 != "":
            cvt = self.convert(dom_type,ir1.data_type)
            new_temp = self.new_temp(ir1.data_type)
            gen3 = f"{new_temp} = {cvt} {ir1.place}"
            ir1.place = new_temp
        ir0.code = self.join(ir2.code, gen1, gen2,gen3)
        ir0.place = ir1.place
        self.debug_print(ir0)

    def arithmetic_expression(self, ir0, ir1, op, ir2):
        dom_type = self.dom_type(ir1.data_type, ir2.data_type)
        ir0.place = self.new_temp(dom_type)
        gen1 = ""
        gen0 = ""
        if ir1.data_type != dom_type:
            t = ir1.place
            ir1.place = self.new_temp(ir1.data_type)
            gen0 = f"{ir1.place} = {t}"
            cvt = self.convert(ir1.data_type,dom_type)
            new_temp = self.new_temp(dom_type)
            gen1 = f"{new_temp} = {cvt}  {ir1.place}"
            ir1.place = new_temp
            gen1 = self.join(gen0,gen1)
        if ir2.data_type != dom_type:
            t = ir2.place
            ir2.place = self.new_temp(ir2.data_type)
            gen0 = f"{ir2.place} = {t}"
            cvt = self.convert(ir2.data_type,dom_type)
            new_temp = self.new_temp(dom_type)
            gen1 = f"{new_temp} = {cvt} {ir2.place}"
            ir2.place = new_temp
            gen1 = self.join(gen0,gen1)
        op = f"({dom_type}) {op}"
        gen2 = f"{ir0.place} = {ir1.place} {op} {ir2.place}"
        ir0.code = self.join(ir1.code, ir2.code,gen1, gen2)
        self.debug_print(ir0)

    def pointer_arithmetic_expression(self, ir0, ir1, op, ir2, c1, c2, d_size=None):
        t_place = self.new_temp('int') # done if ir2 is an int.
        
        val = 8
        if c1 != 0: # ir1 is n-dimensional pointer
            ir0.place = self.new_temp(ir1.data_type)
            if c1 == 1:
                val = d_size
            gen0 = ""
            if ir2.data_type != 'int': # pointer arithmetic type conversion to int
                cvt = f"{ir2.data_type}Toint"
                type_cast_place = self.new_temp('int')
                gen0 = f"{type_cast_place} = {cvt} {ir2.place}"
                ir2.place = type_cast_place
            gen0 = self.join(gen0 , f"{t_place} = {ir2.place} (long_long) * {val}")
            gen1 = f"{ir0.place} = {ir1.place} (long_long) {op} {t_place}"
        else:
            ir0.place = self.new_temp(ir2.data_type)
            if c2 == 1: # ir2 is n-dimensional pointer
               val = d_size
            gen0 = ""
            if ir1.data_type != 'int':
                cvt = f"{ir1.data_type}Toint"
                type_cast_place = self.new_temp('int')
                gen0 = f"{type_cast_place} = {cvt} {ir1.place}"
                ir1.place = type_cast_place
            gen0 = self.join(gen0, f"{t_place} = {ir1.place} (long_long) * {val}")
            gen1 = f"{ir0.place} = {ir2.place} (long_long) {op} {t_place}"
        ir0.code = self.join(ir1.code, ir2.code, gen0 , gen1)

    def bitwise_expression(self, ir0, ir1, op, ir2):
        ir0.place = self.new_temp(ir0.data_type)
        gen = f"{ir0.place} = {ir1.place} ({ir1.data_type}) {op} {ir2.place}"
        ir0.code = self.join(ir1.code, ir2.code, gen)
        self.debug_print(ir0)
    
    def relational_expression(self, ir0, ir1, op, ir2):
        print(ir1.data_type, ir2.data_type)
        ir0.place = self.new_temp(ir0.data_type)
        dom_type = "" if "*" in ir1.data_type and "*" in ir2.data_type else self.dom_type(ir1.data_type, ir2.data_type).replace(' ','_') 
        gen1 = ""

        if ir1.data_type!= dom_type:
            t = ir1.place
            ir1.place = self.new_temp(ir1.data_type)
            gen0 = f"{ir1.place} = {t}"
            cvt = self.convert(ir1.data_type,dom_type)
            new_temp = self.new_temp(dom_type)
            gen1 = f"{new_temp} = {cvt} {ir1.place}"
            ir1.place = new_temp
            gen1 = self.join(gen0,gen1)
        
        elif ir2.data_type != dom_type:
            t = ir2.place
            ir2.place = self.new_temp(ir2.data_type)
            gen0 = f"{ir2.place} = {t}"
            cvt = self.convert(ir2.data_type,dom_type)
            new_temp = self.new_temp(dom_type)
            gen1 = f"{new_temp} = {cvt} {ir2.place}"
            ir2.place = new_temp
            gen1 = self.join(gen0,gen1)
            
        op = f"({ir0.data_type}) {op}"
        gen2 = f"{ir0.place} = {ir1.place} {op} {ir2.place}"
        ir0.code = self.join(ir1.code, ir2.code, gen1,gen2)
        self.debug_print(ir0)    

    def inc_dec(self, ir0, ir1, op, post=False):
        gen1 = ""
        if post:
            ir0.place = self.new_temp(ir0.data_type)
            gen1 = f"{ir0.place} = {ir1.place}"
        else:
            ir0.place = ir1.place
        op = op[0]
        dom_type = self.dom_type(ir0.data_type, ir1.data_type)
        gen3=""
        one = 1
        if dom_type != 'int':
            t = one
            one = self.new_temp(dom_type)
            gen0 = f"{one} = {t}"
            cvt = self.convert('int',dom_type)
            new_temp = self.new_temp(dom_type)
            gen3 = f"{new_temp} = {cvt} {one}"
            one = new_temp
            gen3 = self.join(gen0,gen3)
        gen2 = f"{ir1.place} = {ir1.place} ({ir0.data_type}) {op} {one}"
        ir0.code = self.join(gen1, gen3, gen2)
        self.debug_print(ir0)

    def unary(self, ir0, ir1, op):
        ir0.place = self.new_temp(ir0.data_type)
        gen = f"{ir0.place} = {op} {ir1.place}"
        ir0.code = self.join(ir1.code, gen)
        self.debug_print(ir0)

    def blockitem(self, ir0, ir1, ir2):
        ir0.code = self.join(ir1.code, ir2.code)
        ir0.falselist += ir1.falselist + ir2.falselist
        ir0.truelist += ir1.truelist + ir2.truelist
        ir0.switchup += ir1.switchup + ir2.switchup
        ir0.switchplace += ir1.switchplace + ir2.switchplace
        ir0.switchdatatype += ir1.switchdatatype + ir2.switchdatatype
        self.debug_print(ir0)
        
    def translation_unit(self, ir0, ir1, ir2):
        ir0.code = self.join(ir1.code, ir2.code)
        self.debug_print(ir0)

    def function_definition(self,ir0,ir1,ir2,func_name,size):
        gen1 = self.new_label(func_name) + ':'
        gen2 = f"BeginFunc {size}"
        gen3 = "EndFunc"
        ir0.code = self.join(gen1,gen2,ir2.code,gen3)
        self.debug_print(ir0)

    def return_jump(self, ir0, ir1):
        gen = f"return {ir1.place}"
        ir0.code = self.join(ir1.code, gen)

    def argument_expression(self, ir0, ir1, ir2):
        ir0.code = self.join(ir1.code, ir2.code)
        ir0.parameters = ir1.parameters + [ir2.place]
    
    def parameter_init(self, ir0, ir1):
        ir0.parameters = [ir1.place]

    def function_call(self, ir0, ir1, ir2, ret,param_size=0,argument_list = [], func_params= []):
        if ir2 is not None:
            # arguments
            gen3 = f"pop params {param_size}"
            new_param_list = []
            if ret == 'void':
                gen0 = ""
                j = 0
                for i in range(0,len(ir2.parameters)):
                    if argument_list[i] == func_params[j].type or func_params[j].type == '...':
                        new_param_list.append(ir2.parameters[i])
                    else:
                        _temp = self.new_temp(func_params[j].type)
                        cvt = self.convert(argument_list[i],func_params[j].type)
                        gen0 = self.join(gen0, f"{_temp} = {cvt} {ir2.parameters[i]}")
                        new_param_list.append(_temp)
                    if j < len(func_params)-1:
                        j += 1                        
                gen1 = ""
                for param in new_param_list:
                    gen1 = self.join(gen1, f"param {param}")
                gen1 = self.join(gen0, gen1)
                gen2 = f"call {ir1.place}, {str(len(ir2.parameters))}"
                ir0.code = self.join(ir2.code, gen1, gen2,gen3)
            else:
                ir0.place = self.new_temp(ir0.data_type)
                gen0 = ""
                j = 0
                for i in range(0,len(ir2.parameters)):
                    if argument_list[i] == func_params[j].type or func_params[j].type == '...':
                        new_param_list.append(ir2.parameters[i])
                    else:
                        _temp = self.new_temp(func_params[j].type)
                        cvt = self.convert(argument_list[i],func_params[j].type)
                        gen0 = self.join(gen0, f"{_temp} = {cvt} {ir2.parameters[i]}")
                        new_param_list.append(_temp)
                    if j < len(func_params)-1:
                        j += 1                        
                gen1 = ""
                for param  in new_param_list:
                    gen1 = self.join(gen1, f"param {param}")
                gen1 = self.join(gen0, gen1)
                gen2 = f"{ir0.place} = call {ir1.place}, {str(len(ir2.parameters))}"
                ir0.code = self.join(ir2.code, gen1, gen2,gen3)
        else:
            if ret == 'void':
                ir0.code = "call " + ir1.place
            else:
                ir0.place = self.new_temp(ir0.data_type)
                gen2 = ir0.place + " = call " + ir1.place + ', ' + str(0)
                ir0.code = self.join(gen2)

    def label_add(self, ir0, label,ir1):
        ir0.code = f"{label}:"
        ir0.code = self.join(ir0.code,ir1.code)

    def goto_label(self, ir0, label):
        ir0.code = f"goto {label}"
    
    def while_loop(self, ir0, ir1, ir2):
        self.manage_lists(ir0,ir2)
        ir0.begin = self.new_label()
        ir0.after = self.new_label()
        if ir1.bpneed>0:
            self.resolve_exp(ir1)
        gen1 = f"{ir0.begin}:"

        new_temp = self.new_temp('int')
        gen22 = ""
        if ir1.data_type != "int":
            gen22 = f"{new_temp} = {self.convert(ir1.data_type, 'int')} {ir1.place}"
            ir1.place = new_temp

        gen2 = f"if {ir1.place} == 0 goto {ir0.after}"
        gen3 = f"goto {ir0.begin}"
        gen4 = f"{ir0.after}:"
        ir0.code = self.join(gen1, ir1.code,gen22, gen2, ir2.code, gen3, gen4)
        for c in ir0.truelist: #handle continue
            self.backpatch(ir0,c,ir0.begin)
        for c in ir0.falselist: #handle break
            self.backpatch(ir0,c,ir0.after)
        self.debug_print(ir0)
    
    def do_while_loop(self, ir0, ir1, ir2):
        self.manage_lists(ir0,ir2)
        ir0.begin = self.new_label()
        ir0.after = self.new_label()
        if ir1.bpneed>0:
            self.resolve_exp(ir1)
        gen1 = f"{ir0.begin}:"

        new_temp = self.new_temp('int')
        gen22=""
        if ir1.data_type != "int":
            gen22 = f"{new_temp} = {self.convert(ir1.data_type, 'int')} {ir1.place}"
            ir1.place = new_temp

        gen2 = f"if {ir1.place} == 0 goto {ir0.after}"
        gen3 = f"goto {ir0.begin}"
        gen4 = f"{ir0.after}:"
        ir0.code = self.join(gen1,ir2.code,ir1.code,gen22,gen2,gen3,gen4)
        for c in ir0.truelist: #handle continue
            self.backpatch(ir0,c,ir0.begin)
        for c in ir0.falselist: #handle break
            self.backpatch(ir0,c,ir0.after)
        self.debug_print(ir0)
    
    def do_until_loop(self, ir0, ir1, ir2):
        self.manage_lists(ir0,ir2)
        ir0.begin = self.new_label()
        ir0.after = self.new_label()
        if ir1.bpneed>0:
            self.resolve_exp(ir1)
        gen1 = f"{ir0.begin}:"

        new_temp = self.new_temp('int')
        gen11=""
        if ir1.data_type != "int":
            gen11 = f"{new_temp} = {self.convert(ir1.data_type, 'int')} {ir1.place}"
            ir1.place = new_temp

        gen2 = f"if {ir1.place} != 0 goto {ir0.after}"
        gen3 = f"goto {ir0.begin}"
        gen4 = f"{ir0.after}:"
        ir0.code = self.join(gen1,ir2.code,ir1.code,gen11,gen2,gen3,gen4)
        for c in ir0.truelist: #handle continue
            self.backpatch(ir0,c,ir0.begin)
        for c in ir0.falselist: #handle break
            self.backpatch(ir0,c,ir0.after)
        self.debug_print(ir0)

    def for_loop(self, ir0, ir1, ir2, ir3, ir4):
        self.manage_lists(ir0,ir3,ir4)
        ir0.begin = self.new_label()
        ir0.cont = self.new_label()  #continue jumps here
        ir0.after = self.new_label()
        gen1 = f"{ir0.begin}:"
        if ir2.bpneed>0:
            self.resolve_exp(ir2)

        new_temp = self.new_temp('int')
        gen11=""
        if ir2.data_type != "int" and ir2.data_type is not None:
            gen11 = f"{new_temp} = {self.convert(ir2.data_type, 'int')} {ir1.place}"
            ir2.place = new_temp
        
        gen2 = f"if {ir2.place} == 0 goto {ir0.after}"
        gen5 = f"{ir0.cont}:"    
        gen3 = f"goto {ir0.begin}"
        gen4 = f"{ir0.after}:"
        if ir3 is not None:
            ir0.code = self.join(ir1.code,gen1,ir2.code,gen11,gen2,ir4.code,gen5,ir3.code,gen3,gen4)
        else:
            ir0.code = self.join(ir1.code,gen1,ir2.code,gen11,gen2,ir4.code,gen5,gen3,gen4)

        for c in ir0.truelist: #handle continue
            self.backpatch(ir0,c,ir0.cont)
        for c in ir0.falselist: #handle break
            self.backpatch(ir0,c,ir0.after)
        
    def if_with_else(self, ir0, ir1, ir2,ir3): #1exp 2statement 3statement
        ir0.after = ir3.after
        gen4 = ""
        if ir1.bpneed>0:
            self.resolve_exp(ir1)
        if ir0.after == "":
            ir0.after = self.new_label()
            gen4 = f"{ir0.after}:"
        ir0.else_ = self.new_label()

        new_temp = self.new_temp('int')
        gen11=""
        if ir1.data_type != "int":
            gen11 = f"{new_temp} = {self.convert(ir1.data_type, 'int')} {ir1.place}"
            ir1.place = new_temp

        gen1 = f"if {ir1.place} == 0 goto {ir0.else_}"
        gen2 = f"goto {ir0.after}"
        gen3 = f"{ir0.else_}:"
        self.manage_lists(ir0,ir2,ir3)
        ir0.code = self.join(ir1.code,gen11,gen1,ir2.code,gen2,gen3,ir3.code,gen4)
    
    def if_no_else(self, ir0, ir1, ir2):
        ir0.after = self.new_label()
        if ir1.bpneed>0:
            self.resolve_exp(ir1)

        new_temp = self.new_temp('int')
        gen11=""
        if ir1.data_type != "int":
            gen11 = f"{new_temp} = {self.convert(ir1.data_type, 'int')} {ir1.place}"
            ir1.place = new_temp

        gen1 = f"if {ir1.place} == 0 goto {ir0.after}"
        gen2 = "" #f"goto {ir0.after}"
        gen4 = f"{ir0.after}:"
        self.manage_lists(ir0,ir2)
        ir0.code = self.join(ir1.code,gen11,gen1,ir2.code,gen2,gen4)

    def ternary(self,ir0,ir1,ir2,ir3): #1 is condition , 2 is true , 3 is false
        if ir1.bpneed>0:
            self.resolve_exp(ir1)
        if ir2.bpneed>0:
            self.resolve_exp(ir2)
        if ir3.bpneed>0:
            self.resolve_exp(ir3)
        false = self.new_label()
        after = self.new_label()
        ir0.place = self.new_temp(ir0.data_type) 

        new_temp = self.new_temp('int')
        gen11=""
        if ir1.data_type != "int":
            gen11 = f"{new_temp} = {self.convert(ir1.data_type, 'int')} {ir1.place}"
            ir1.place = new_temp

        gen1 = f"if {ir1.place} == 0 goto {false}"
        gen2 = f"{ir0.place} = {ir2.place}" #true
        gen3 = f"goto {after}"
        gen4 = f"{false}:"
        gen5 = f"{ir0.place} = {ir3.place}" #false
        gen6 = f"{after}:"
        ir0.code = self.join(ir1.code,gen11,gen1,ir2.code,gen2,gen3,gen4,ir3.code,gen5,gen6)

    def resolve_exp(self,ir1): #falselist truelist assign them to its place , new label
        true = self.new_label()
        false = self.new_label()
        start = self.new_label()
        var = self.new_temp('int')
        gen0 = ""

        new_temp = self.new_temp('int')
        gen11=""
        if ir1.data_type != "int":
            gen11 = f"{new_temp} = {self.convert(ir1.data_type, 'int')} {ir1.place}"
            ir1.place = new_temp

        gen1 = f"if {ir1.place} == 0 goto {false}"
        gen2 = f"{true}:"
        gen3 = f"{var} = 1"
        gen4 = f"goto {start}"
        gen5 = f"{false}:"
        gen6 = f"{var} = 0"
        gen7 = f"{start}:"
        gen8 = ""
        ir1.place = var
        for c in ir1.truelist:
            self.backpatch(ir1,c,true)
        for c in ir1.falselist:
            self.backpatch(ir1,c,false)
        ir1.code = self.join(ir1.code,gen0,gen11,gen1,gen2,gen3,gen4,gen5,gen6,gen7,gen8)
    
    def logical_and(self,ir0,ir1,op,ir2):
        falsego = self.bp_label() #go outside if, forloop
        mid = self.new_label() #where && ka lhs should jump if true
        
        new_temp = self.new_temp('int')
        gen11=""
        if ir1.data_type != "int":
            gen11 = f"{new_temp} = {self.convert(ir1.data_type, 'int')} {ir1.place}"
            ir1.place = new_temp
        
        gen = f"if {ir1.place} == 0 goto {falsego}" #lhs false go out
        ir0.falselist += [falsego] #lhs false then go out , will be backpatced in IF
        for c in ir1.truelist: #lhs ka true jumpshere
            self.backpatch(ir1,c,mid)
        ir0.falselist += ir1.falselist #lhs ka false also jumps out
        #rhs ka true is added to truelist , coz rhs true then jumps to somewhere directly
        ir0.truelist +=ir2.truelist
        #rhs ka false goes out directly
        ir0.falselist += ir2.falselist
        ir0.bpneed += ir1.bpneed + ir2.bpneed + 1
        gen2 = f"{mid}:"
        ir0.place = ir2.place #ir1 is true so pass ir2 for further eval
        ir0.code = self.join(ir1.code,gen11,gen,gen2,ir2.code)
        self.debug_print(ir0)

    def logical_or(self,ir0,ir1,op,ir2): # when true then we jump to the inside scope , using truelist
        truego = self.bp_label()
        ir0.bpneed += ir1.bpneed + ir2.bpneed + 1
        mid = self.new_label()

        new_temp = self.new_temp('int')
        gen11=""
        if ir1.data_type != "int":
            gen11 = f"{new_temp} = {self.convert(ir1.data_type, 'int')} {ir1.place}"
            ir1.place = new_temp

        gen = f"if {ir1.place} != 0 goto {truego}" #first statement true so go inside scope
        gen2 = f"{mid}:"
        for c in ir1.falselist: #lhs ka false jumpshere
            self.backpatch(ir1,c,mid)
        ir0.truelist += [truego] #false hua toh go to net statement
        ir0.truelist += ir1.truelist + ir2.truelist
        ir0.falselist += ir2.falselist
        ir0.place = ir2.place #ir1 is false so pass ir2 and if that false then jump
        ir0.code = self.join(ir1.code,gen11,gen,gen2,ir2.code)
        return 

    def backpatch(self,ir1,find,target):
        ir1.code = ir1.code.replace(find, target)

    def unary_not(self, ir0, ir1, op):
        ir0.place = self.new_temp('int') # check here ?
        new_temp = self.new_temp('int')

        gen1 = ""
        if ir1.data_type != "int":
            gen1 = f"{new_temp} = {self.convert(ir1.data_type, 'int')} {ir1.place}"
            ir1.place = new_temp
        gen = f"{ir0.place} = {op} {ir1.place}"
        ir0.truelist = ir1.falselist
        ir0.falselist = ir1.truelist
        ir0.code = self.join(ir1.code, gen1, gen)
        ir0.data_type = "int"
        # self.debug_print(ir0)

    def unary_ptr(self, ir0, ir1, op):
        gen1=""
        if ir1.place[0] == '*':
            temp1 = self.new_temp(ir1.data_type)
            gen1 = f"{temp1} = {ir1.place}"
            ir0.place=f"*{temp1}"
        else:
            ir0.place=f"*{ir1.place}"
        ir0.code = self.join(ir1.code,gen1)

    def call_array_position(self, ir0, ir1, ir2, dimensions):
        gen2=""
        # print(ir0.place,ir1.place,ir2.place)
        ir0.place = self.new_temp('long_long')
        print(ir0.data_type,'jhbdfsgfffffffffffdsh')
        if ir1.place[0] != "@":
            # gen0 
            gen1 = f"{ir0.place} = {ir2.place}"
        else:
            gen1 = f"{ir0.place} = {ir1.place} (long_long) + {ir2.place}"
            
        if(len(dimensions)>0):
            gen2 = f"{ir0.place} = {ir0.place} (long_long) * {dimensions[0]}"
        ir0.code = self.join(ir1.code,ir2.code,gen1,gen2) 
        self.debug_print(ir0)

    def unary_array(self, ir0, ir1, var,size):
        new_temp = self.new_temp('*'+ir0.data_type)
        ir0.place = f"*{new_temp}"
        gen = f"{ir1.place} = {ir1.place} (long_long) * {size}"
        arra= self.new_temp('long_long')
        gen11 = f"{arra} = & {var}"
        var = arra
        gen1 = f"{new_temp} = {var} (long_long) + {ir1.place}"
        ir0.code = self.join(ir1.code,gen, gen11,gen1)
        self.debug_print(ir0)

    def initializer(self, ir0, ir1):
        if ir1.place is not None:
            ir0.initializer_list.append(ir1.place)
        ir0.code = ir1.code

    def initializer_list(self, ir0, ir1, ir2):
        ir0.initializer_list = copy.deepcopy(ir1.initializer_list)
        if(len(ir2.initializer_list) > 0):
            ir0.initializer_list += ir2.initializer_list
        elif(ir2.place is not None):
            ir0.initializer_list.append(ir2.place)
        ir0.code = self.join(ir1.code, ir2.code)

    def array_declarator(self, ir0, ir1, ir2):
        ir0.place = ir1.place

    def array_initializer_list(self, ir0, ir1, ir2, size,type_size):
        array = ir1.place
        initializations = []
        max_size = size

        ptr = 0
        if ptr < len(ir2.initializer_list):
            for _ in range(int(max_size)):
                label = self.new_temp('long_long')
                gen = f"{label} = {ptr} (long_long) * {type_size}\n"
                
                new_temp = self.new_temp('*'+ir1.data_type)
                gen += f"{new_temp} = {array} (long_long) + {label}\n"
                
                gen += f"*{new_temp}"
                gen += f" = {ir2.initializer_list[ptr]}"

                initializations.append(gen)

                ptr += 1
                if ptr == len(ir2.initializer_list):
                    break

        ir0.code = self.join(ir1.code, ir2.code)
        for initialization in initializations:
            ir0.code = self.join(ir0.code, initialization)


    def switch_labeled_statement(self,ir0,ir1,ir2): #ir1 is condition , ir2 is statement code
        ir0.switchup = [ir1.code]
        ir0.switchplace = [ir1.place]
        ir0.switchdatatype = [ir1.data_type]
        true= self.new_label()
        ir0.truelist = [true]
        gen1 = f"{true}:"
        ir0.code=self.join(gen1,ir2.code)


    def default_labeled_statement(self,ir0,ir1): #no condition coz default, ir1 is statement code
        ir0.switchup = ["default"]
        ir0.switchplace = ["default"]
        ir0.switchdatatype = ["default"]
        true= self.new_label()
        ir0.truelist = [true]
        ir0.falselist += ir1.falselist
        gen1 = f"{true}:"
        ir0.code=self.join(gen1,ir1.code)

    def break_jump(self,ir0):
        temp = self.bp_label()
        ir0.code = f"goto {temp}"
        ir0.falselist = [temp]

    def continue_jump(self,ir0):
        temp = self.bp_label()
        ir0.code = f"goto {temp}"
        ir0.truelist = [temp]

    def manage_lists(self,ir0,*args):
        for c in args:
            if c is not None:
                ir0.falselist += c.falselist
                ir0.truelist += c.truelist

    def switch_selection_statement(self,ir0,ir1,ir2): #ir1 has variable , ir2 has statements
        gen1 = ""
        for up, true, place, place_data_type in zip(ir2.switchup,ir2.truelist,ir2.switchplace, ir2.switchdatatype):
            if(place!="default"):
                dominating_type = self.dom_type(place_data_type, ir1.data_type)
                
                gen0 = ""
                if dominating_type != ir1.data_type:
                    new_temp = self.new_temp(dominating_type)
                    gen0 = f"{new_temp} = ({self.convert(ir1.data_type, dominating_type)}) {ir1.place}"
                elif dominating_type != place_data_type:
                    new_temp = self.new_temp(place_data_type)
                    gen0 = f"{new_temp} = {place}"
                    new_temp2 = self.new_temp(dominating_type)
                    gen3 = f"{new_temp2} = ({self.convert(place_data_type, dominating_type)}) {new_temp}"
                    gen0 = self.join(gen0, gen3)
                    place = new_temp2

                gen2 = f"if {place} == {ir1.place} goto {true}"
                gen1 = self.join(gen0,gen1,up,gen2)
            else:
                gen2 = f"goto {true}"
                gen1 = self.join(gen1,gen2)

        temp = self.new_label()
        gen3=f"{temp}:"
        for c in ir2.falselist:
            self.backpatch(ir2,c,temp)
        ir0.code = self.join(ir1.code,gen1,ir2.code,gen3)

    def struct_access(self,ir0,ir1,offset,isArrow=False,isArray=False,max_sz=None):
        ir0.place = self.new_temp('*'+max_sz)
        if isArrow:
            gen1 = f"{ir0.place} = {ir1.place}"
        else:
            gen1 = f"{ir0.place} = & {ir1.place}"
        gen2 = f"{ir0.place} = {ir0.place} (long_long) + {offset}"
        # gen3 = f"*{ir0.place}"
        if not isArray: 
            ir0.place = '*'+ir0.place
        ir0.code = self.join(gen1,gen2)

    def struct_init_list(self,ir0,ir1,offset_list,init_list,max_sz = None):
        ir0.place = self.new_temp('*'+ max_sz)
        gen1 = f"{ir0.place} = & {ir1.place}"
        for i in range(0,len(init_list)):
            #size of this is always <= size of offset since we have done semantic checks
            gen_temp = f"{ir0.place} = {ir0.place} (long_long) + {offset_list[i]}"
            gen_temp2 = f"*{ir0.place} = {init_list[i]}"
            gen1 = self.join(gen1,gen_temp,gen_temp2)
        ir0.code = gen1

    def cast_expression(self, ir0, cast_type ,ir1):
        ir0.place = self.new_temp(cast_type)
        gen = ""
        if cast_type != ir1.data_type:
            cvt = self.convert(ir1.data_type,cast_type)
            gen = f"{ir0.place} = {cvt} {ir1.place}"
        ir0.code = self.join(ir1.code,gen)