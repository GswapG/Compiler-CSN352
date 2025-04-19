from .register_allocator import *

class Instruction:
    def __init__(self, inst):
        self.text = str(inst)
        self.inst = []
        self.is_goto = False
        self.is_if = False
        self.is_param = False
        self.is_function_call = False
        self.is_return = False
        self.is_pop = False
        self.is_begin = False
        self.is_end = False
        self.is_assignment = False
        self.is_cast = False
        self.is_operation = False
        self.parse_inst()

    def parse_inst(self):
        inst = self.text.split(' ')
        self.inst = inst
        if 'BeginFunc' in inst:
            self.is_begin = True
        elif 'EndFunc' in inst:
            self.is_end = True
        elif 'return' in inst:
            self.is_return = True
        elif 'param' in inst:
            self.is_param = True
        elif 'call' in inst:
            self.is_function_call = True
        elif 'pop' in inst:
            self.is_pop = True

        if '=' not in inst:
            return 
        # = hai
        if len(inst) <= 3:
            # assignment
            self.is_assignment = True
        elif len(inst) <= 4:
            # cast
            self.is_cast = True
        else:
            # some operator or call
            if 'call' in inst:
                self.is_assignment = True
            else:
                # some operator
                self.is_operation = True
        
class CodeGenerator:
    def __init__(self):
        pass