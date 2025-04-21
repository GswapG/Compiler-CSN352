from .register_allocator import RegisterAllocator
from .cfg import *
from .register import init_gpr

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
    """
    All handler functions take in inst as input (even if they do not use it)
    """
    def __init__(self, cfg: CFG, output_stream):
        self.cfg = cfg
        self.out = output_stream
        self.reg_allocator = RegisterAllocator(init_gpr())
    
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
    
    def emit(self,code):
        self.out.write(code)

    def generate_code(self):
        """
        Iterates through blocks from cfg,
        Iterates through inst in block and calls the repective function based on type of instruction
        """
        pass
    
    def handle_goto(self, inst):
        pass
    def handle_if(self, inst):
        pass
    def handle_param(self, inst):
        pass
    def handle_return(self, inst):
        pass
    def handle_call(self, inst):
        pass
    def handle_assignment(self, inst):
        pass
    def handle_operation(self, inst):
        pass
    def handle_begin(self, inst):
        codel1 = f'push rbp'
        codel2 = f'mov rbp, rsp'
        code = self.join(codel1, codel2)
        self.emit(code)
    
    def handle_end(self, inst):
        codel1 = f'leave'
        codel2 = f'ret'
        code = self.join(codel1, codel2)
        self.emit(code)

    def get_arithmetic_instruction(self, op: str) -> str:
        """
        Map arithmetic operator to assembly instruction.
        """
        return {
            '+': 'add',
            '-': 'sub',
            '*': 'imul',   
            '/': 'idiv',   
            '%': 'idiv'    # Modulo uses the same idiv, result in rdx
        }.get(op, None)

    def get_jump_instruction(self, relop: str) -> str:
        """
        Map relational operator to assembly jump instruction.
        """
        return {
            '<': 'jl',
            '<=': 'jle',
            '>': 'jg',
            '>=': 'jge',
            '==': 'je',
            '!=': 'jne'
        }.get(relop, 'jmp')