from .register_allocator import RegisterAllocator
from .cfg import *
from .register import *
import os
from collections import defaultdict

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
        self.label = None
        self.used_vars = []
        self.parse_inst()
        self.update_use()

    def parse_inst(self):
        inst = self.text.split(' ')
        self.inst = inst
        if inst[0][-1] == ':':
            # label present
            self.label = inst[0][:-1]
            self.inst = inst[1:]
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

    def update_use(self):
        if '=' in self.inst:
            rhs = self.inst[2:]
            for elem in rhs:
                if elem[0] == '@' or '#' in elem:
                    self.used_vars.append(elem) 
        print(self.used_vars)
    
    def has_label(self):
        if self.label is not None:
            return True
        return False
    
    def __str__(self):
        return self.text
        
class CodeGenerator:
    """
    All handler functions take in inst as input (even if they do not use it)
    """
    def __init__(self, cfg: CFG, output_stream):
        self.cfg = cfg
        self.out = output_stream
        self.reg_allocator = RegisterAllocator(init_gpr(),self)
        self.curr_alignment = 0
    
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
        Iterates through inst in block and updates next use info
        """
        for block in self.cfg.basic_blocks:
            print("In block : ", block.block_id)
            # calculate next use
            next_use = defaultdict(int)
            for i in range(len(block.instructions)-1,0,-1):
                instr = Instruction(block.instructions[i])
                for var in instr.used_vars:
                    next_use[var] += 1
            # set next use
            self.reg_allocator.set_next_use(next_use)
            print(next_use)
            # actual iteration of instructions
            for instruction in block.instructions:
                instr = Instruction(instruction)
                print(instr)
                self.handle_instruction(instr)

    
    def handle_instruction(self, inst: Instruction):
        """
        Calls different handlers based on different instruction type
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
    
def driver(filename, graphgen):
    if filename[-2:] in ('.c','.C'):
        filename = filename[:-2]
    filename += '.tac'
    file_path = os.path.join("./generatedIR/",filename)
    IR = ir_input(file_path)
    cff = CFF(IR)
    if graphgen:
        graph_path = os.path.join('./generatedCFG', filename)
        cff.visualize_all_cfgs(graph_path)
    for i, cfg in enumerate(cff.cfgs):
        print("In cfg : ", i)
        output_path = "./generatedASM/"
        filename = filename.split('.')[0] + '.asm'
        output_path = os.path.join(output_path,filename)
        with open(output_path, 'a') as generated_asm:
            generator = CodeGenerator(cfg,generated_asm)
            generator.generate_code()
        print("===================================")