from .register_allocator import RegisterAllocator
from .cfg import *
from .register import *
import os
from collections import defaultdict
from ..address_map import AddressMap
from ..size_map import SizeMap
from ..utils import get_size_from_type
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
        self.is_assigned_call = False
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
            # check to make sure label is not function name
            if not inst[0][0] == '.':
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
        elif 'goto' in inst:
            self.is_goto = True

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
                self.is_assignment = False
                self.is_call = False
                self.is_assigned_call = True
            else:
                # some operator
                self.is_assignment = False
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
    def __init__(self, cfg: CFG, output_stream, address_map: AddressMap,size_map: SizeMap):
        self.cfg = cfg
        self.out = output_stream
        self.address_map = address_map
        self.size_map = size_map
        self.reg_allocator = RegisterAllocator(init_gpr(),self)
        self.curr_alignment = 0
        self.size_specifiers = ['qword','dword','word','byte','byte']
    
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
    
    def get_size_idx(self, type=None,size=None):
        if size:
            sz = size
        elif type:
            sz = get_size_from_type(type)
        return {
            8:0,
            4:1,
            2:2,
            1:3
        }.get(sz)
    
    def is_constant(self, t2):
        if t2.isnumeric():
            # int constant
            size = 1
        elif t2[0] == "'":
            # char constant
            size = 3
        elif t2[0] == '"':
            # string constant
            size = 0
        else:
            return False
        return True
    
    def emit(self, code):
        """
        Writes the given code to the output stream with proper indentation.
        Labels are not indented, while other instructions are indented with a tab.
        """
        if code.endswith(':') or code[0] == ';':  # Check if the code is a label
            self.out.write(f'{code}\n')  # No indentation for labels
        else:
            self.out.write(f'\t{code}\n')  # Add a tab for instructions

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
        print("Handling instruction: ", inst.text)
        if inst.has_label():
            label = inst.label
            code = f'{label}:'
            self.emit(code)
        # check for different types of instructions
        if inst.is_begin:
            self.handle_begin(inst)
        elif inst.is_end:
            self.handle_end(inst)
        elif inst.is_goto:
            self.handle_goto(inst)  
        elif inst.is_if:
            self.handle_if(inst)
        elif inst.is_param:
            self.handle_param(inst)
        elif inst.is_return:
            self.handle_return(inst)
        elif inst.is_function_call:
            self.handle_call(inst)
        elif inst.is_assignment:
            self.handle_assignment(inst)
        elif inst.is_cast:
            self.handle_cast(inst)
        elif inst.is_operation:
            self.handle_operation(inst)
        # else:
        #     return
        #     raise Exception("Unknown instruction type")
        print(self.reg_allocator.add_desc)
        print(self.reg_allocator.reg_desc)
        
    def handle_goto(self, inst):
        code = f'jmp {inst.inst[1]}'
        self.emit(code)

    def handle_cast(self, inst):
        pass
    def handle_if(self, inst):
        pass
    def handle_param(self, inst):
        pass
    def handle_return(self, inst):
        pass
    def handle_call(self, inst):
        code = f'call {inst.inst[1][:-1]}'
        self.emit(code)

    def handle_assignment(self, inst):
        # check if second element is a variable or a constant
        # if it is a variable, get the register for it
        # if it is a constant, mov instruction is needed
        t2 = inst.inst[2]
        t1 = inst.inst[0]
        if t2[0] == '@' or '#' in t2:
            if t1[0] == '@':
                # t1 is temp
                reg1, reg2 = self.reg_allocator.get_register(inst)
                # dono register me hai to inke bas register aur address descriptors update karne hain, no code emitted
                # reg2 ko t1 ke reg ke liye use karna hai
                self.reg_allocator.add_desc.set_entry_to_reg(t1, reg2)
                self.reg_allocator.reg_desc.add_var_to_register(reg2, t1)
            else:
                # t1 is named
                address = self.address_map.get_address(t1)
                regs = self.reg_allocator.add_desc.get_reg_allocated(t1)
                if regs:
                    for reg in regs:
                        self.reg_allocator.reg_desc.discard_from_reg(reg,t1)
                self.reg_allocator.add_desc.set_mem(t1)
                self.reg_allocator.remove_registers(t1)
                reg = self.reg_allocator.get_register(inst)
                if reg:
                    # t2 in reg
                    reg = reg[0]
                    size = self.get_size_idx(size=self.size_map.get_size(t1))
                    code = f'mov {self.size_specifiers[size]} [rbp{address}], {reg[size]}'
                    self.emit(code)
        else:
            # constant, some code is generated for it
            size = 0
            if t2.isnumeric():
                # int constant
                size = 1
            elif t2[0] == "'":
                # char constant
                size = 3
                t2 = ord(t2[1])
            elif t2[0] == '"':
                # string constant
                size = 0
            if t1[0] == '@':
                # temp
                reg, = self.reg_allocator.get_register(inst)
                code = f'mov {reg[size]}, {t2}'
                self.emit(code)
            else:
                address = self.address_map.get_address(t1)
                self.reg_allocator.add_desc.set_mem(t1)
                self.reg_allocator.remove_registers(t1)
                code = f'mov {self.size_specifiers[size]} [rbp{address}], {t2}'
                self.emit(code)

    def handle_operation(self, inst):
        # t1 = t2 (type) op t3
        # at least one of the two operands is a variable (constant folding)
        t1 = inst.inst[0]
        t2 = inst.inst[2]
        t3 = inst.inst[5]
        op = inst.inst[4]
        if self.is_constant(t2):
            # swap t2 and t3 if t2 is constant
            inst.inst[5],inst.inst[2] = inst.inst[2], inst.inst[5]
            t2, t3 = t3, t2 
        if self.is_constant(t3):
            reg, = self.reg_allocator.get_register(inst)
            size = self.get_size_idx(inst.inst[3][1:-1])
            opcode = self.get_arithmetic_instruction(op)
            code = f'{opcode} {reg[size]}, {t3}'
            self.emit(code)
        else:
            reg1, reg2 = self.reg_allocator.get_register(inst)
            size = self.get_size_idx(inst.inst[3][1:-1])
            opcode = self.get_arithmetic_instruction(op)
            code = f'{opcode} {reg1[size]}, {reg2[size]}'
            self.emit(code)

    def handle_begin(self, inst):
        function_name = self.cfg.func_name
        comment = f'; Function {function_name}'
        codel1 = f'{function_name}:'
        codel2 = f'push rbp'
        codel3 = f'mov rbp, rsp'
        self.emit(comment)
        self.emit(codel1)
        self.emit(codel2)
        self.emit(codel3)
    
    def handle_end(self, inst):
        codel1 = f'leave'
        codel2 = f'ret'
        self.emit(codel1)
        self.emit(codel2)

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
    
def driver(filename, graphgen, address_map,size_map):
    if filename[-2:] in ('.c','.C'):
        filename = filename[:-2]
    filename += '.tac'
    file_path = os.path.join("./generatedIR/",filename)
    IR = ir_input(file_path)
    cff = CFF(IR)
    if graphgen:
        graph_path = os.path.join('./generatedCFG', filename)
        cff.visualize_all_cfgs(graph_path)
    output_path = "./generatedASM/"
    filename = filename.split('.')[0] + '.asm'
    output_path = os.path.join(output_path,filename)
    with open(output_path, 'w') as generated_asm:
        generated_asm.write("section .text\n")
        generated_asm.write("global main\n")
        generated_asm.write("extern printf\n")
        generated_asm.write("extern scanf\n")
        generated_asm.write("extern malloc\n")
        generated_asm.write("extern free\n")
        generated_asm.write("extern exit\n")
    for i, cfg in enumerate(cff.cfgs):
        print("In cfg : ", i)
        with open(output_path, 'a') as generated_asm:
            generator = CodeGenerator(cfg,generated_asm,address_map,size_map)
            generator.generate_code()
        print("===================================")