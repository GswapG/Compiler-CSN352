from .register_allocator import RegisterAllocator
from .cfg import *
from .register import *
import os
from collections import defaultdict
from ..address_map import AddressMap
from ..param_map import ParameterMap
from ..size_map import SizeMap
from ..utils import get_size_from_type

class Instruction:
    def __init__(self, inst):
        self.text = str(inst)
        self.inst = []
        self.is_goto = False
        self.is_if = False
        self.is_param = False
        self.is_addr = False
        self.is_function_call = False
        self.is_return = False
        self.is_pop = False
        self.is_begin = False
        self.is_end = False
        self.is_assignment = False
        self.is_assigned_call = False
        self.is_cast = False
        self.is_operation = False
        self.is_relop = False
        self.is_array_deref = False
        self.label = None
        self.used_vars = []
        self.is_deref = False
        self.parse_inst()
        self.update_use()

    def split_instruction(self, text: str) -> list:
        """
        Splits instruction on whitespace while preserving string literals.
        Args:
            text: The instruction text to split
        Returns:
            list: List of instruction components
        """
        result = []
        current = []
        in_string = False
        quote_char = None
        
        for char in text:
            if char in ['"', "'"]:
                if not in_string:
                    # Start of string
                    in_string = True
                    quote_char = char
                    current.append(char)
                elif char == quote_char:
                    # End of string
                    in_string = False
                    current.append(char)
                    result.append(''.join(current))
                    current = []
                    quote_char = None
                else:
                    # Quote character inside string
                    current.append(char)
            elif char.isspace():
                if in_string:
                    current.append(char)
                elif current:
                    result.append(''.join(current))
                    current = []
            else:
                current.append(char)
                
        if current:
            result.append(''.join(current))
            
        return result

    def parse_inst(self):
        inst = self.split_instruction(self.text)
        self.inst = inst
        self.map = ('==','!=','<=','>=','<','>')
        if inst[0][-1] == ':':
            # label present
            # check to make sure label is not function name
            if not inst[0][0] == '.':
                self.label = inst[0][:-1]
                self.inst = inst[1:]
                inst = self.inst
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
        elif 'if' in inst:
            self.is_if = True
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
                self.is_function_call = False
                self.is_assigned_call = True
            else:
                # some operator
                self.is_assignment = False
                self.is_operation = True
                
        for elem in inst:
            if elem in self.map:
                self.is_relop = True
                self.is_assignment = False # maybe not needed because of order of calls but just to be sure
                self.is_operation = False
                break
            if '&' in elem:
                self.is_addr = True
                self.is_assignment = False
                self.is_operation = False
                self.is_relop = False
                break
            if elem.startswith('*') and elem != '*' and "To" not in elem:
                self.is_deref = True
                self.is_assignment = False
                self.is_operation = False
                """
                
                t0 =
                t0 = *t1 + 1

                """

                
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
    def __init__(self, cfg: CFG, output_stream, address_map: AddressMap,size_map: SizeMap, param_map: ParameterMap, type_map):
        self.cfg = cfg
        self.out = output_stream
        self.address_map = address_map
        self.size_map = size_map
        self.param_map = param_map
        self.type_map = type_map
        self.reg_allocator = RegisterAllocator(init_gpr(),self)
        self.curr_alignment = 0
        self.param_regs = init_param_registers()
        self.size_specifiers = ['qword','dword','word','byte','byte']
        self.last_rel_op = None
        self.is_first_param = True
    
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
        elif inst.is_if:
            self.handle_if_SET(inst)
            # self.handle_if(inst)
        elif inst.is_goto:
            self.handle_goto(inst)  
        elif inst.is_param:
            self.handle_param(inst)
        elif inst.is_return:
            self.handle_return(inst)
        elif inst.is_function_call:
            self.handle_call(inst)
        elif inst.is_assigned_call:
            self.handle_assigned_call(inst)
        elif inst.is_addr:
            self.handle_addr(inst)
        elif inst.is_relop:
            # self.handle_relop_SET(inst)
            self.handle_relop(inst)
        elif inst.is_assignment:
            self.handle_assignment(inst)
        elif inst.is_cast:
            self.handle_cast(inst)
        elif inst.is_operation:
            self.handle_operation(inst)
        elif inst.is_deref:
            self.handle_deref(inst)
        # else:
        #     return
        #     raise Exception("Unknown instruction type")
        # print(self.reg_allocator.add_desc)
        # print(self.reg_allocator.reg_desc)
        
    def handle_goto(self, inst):
        code = f'jmp {inst.inst[1]}'
        self.emit(code)

    def handle_deref(self, inst):
        if inst.inst[2][0] == '*':

            pass
        else:
            pass

    def handle_cast(self, inst):
        pass


    def handle_addr(self, inst):
        '''lea into the reg/mem corresponding to t1'''
        '''arrays unsure?'''
        # t1 = & t2
        t1 = inst.inst[0]
        t2 = inst.inst[3]
        # check if t1 is in reg
        size = self.get_size_idx(size=8)

        reg_list = self.reg_allocator.add_desc.get_reg_allocated(t1)
        if reg_list:
            reg = reg_list[0]
        else:
            # Assign a new register for t1
            reg,_ = self.reg_allocator.get_register(inst)
            self.reg_allocator.add_desc.set_entry_to_reg(t1, reg)
            self.reg_allocator.reg_desc.add_var_to_register(reg, t1)
            # Emit the LEA instruction to load the address of t2 into the register
        address = self.address_map.get_address(t2)
        self.emit(f"lea {reg[size]}, [rbp{address}]")

    def handle_array(self,inst):
        '''Parsing of this is left!!'''
        #3AC of arr can be of 2 forms:
        # t1[t2] = t3[t4]
        # t1[t2] = t3
        '''
        *(p+1) = *(p+2)
        '''
        pass

    def handle_if_SET(self, inst):
        # if t1 == 0 goto L5
        # if t1 !=0 goto L6
        t1 = inst.inst[1]
        jmp_label = inst.inst[5]
        size = self.get_size_idx(type='int')
        reg2_list = self.reg_allocator.add_desc.get_reg_allocated(t1)
        if reg2_list:
            reg2 = reg2_list[0]
            self.emit(f'cmp {reg2[size]}, 0')
        else:
            address = self.address_map.get_address(t1)
            self.emit(f'cmp {self.size_specifiers[size]} [rbp{address}], 0')

        if inst.inst[2] == '==':
            self.emit(f'je {jmp_label}')
        else:
            self.emit(f'jne {jmp_label}')
        pass

    def handle_if(self, inst):
        '''Granth ka backpatching in someplaces messes with this logic, this is a failsafe use SET version instead'''
        '''get the required relop instruction'''
        # if @t1 == 0 goto $L6
        # or if @t1 != 0 goto $L6
        if self.last_rel_op is None:
            raise CompileException("No relop found for if statement")
        
        t1 = inst.inst[1]
        op = inst.inst[2]
        jump_label = inst.inst[5]
        if op == '==':
            code = f'{self.get_inverse_jump_instruction(self.last_rel_op)} {jump_label}'
            self.emit(code)
        else:
            code = f'{self.get_jump_instruction(self.last_rel_op)} {jump_label}'
            self.emit(code)

    def handle_param(self, inst):
        pass
        
    def handle_return(self, inst):
        pass

    def handle_call(self, inst):
        code = f'call {inst.inst[1][:-1]}'
        self.emit(code)

    def handle_assigned_call(self, inst):
        code = f'call {inst.inst[3][:-1]}'
        self.emit(code)
        # TODO: check if return value is in rax or xmm0 or something else
    
    def handle_relop(self, inst):
        # t1 = t2 (type) relop t3
        self.last_rel_op = inst.inst[4]
        t1 = inst.inst[0]
        t2 = inst.inst[2]
        t3 = inst.inst[5]
        
        t2_is_const = self.is_constant(t2)
        t3_is_const = self.is_constant(t3)
        
        type = inst.inst[3][1:-1]
        size = self.get_size_idx(type=type)
        '''
        size = self.get_size_idx(type=self.size_map.get_size(t2)) if not t2_is_const else \
            self.get_size_idx(size=self.size_map.get_size(t3)) if not t3_is_const else \
            1  # Default size if both are constants
        '''
        
        if t2_is_const and t3_is_const:
            # Both are constants - compare directly
            self.emit(f'cmp {t2}, {t3}')
        elif t2_is_const:
            # t2 is constant, t3 is variable
            reg3_list = self.reg_allocator.add_desc.get_reg_allocated(t3)
            if reg3_list:
                # t3 is in register
                reg3 = reg3_list[0]
                self.emit(f'cmp {t2}, {reg3[size]}')
            elif t3 in self.address_map.addr_desc:
                # t3 is in memory
                address = self.address_map.get_address(t3)
                self.emit(f'cmp {self.size_specifiers[size]} [rbp{address}], {t2}')
            else:
                raise CompileException(f"Variable {t3} not found in registers or memory")
        elif t3_is_const:
            # t3 is constant, t2 is variable
            reg2_list = self.reg_allocator.add_desc.get_reg_allocated(t2)
            if reg2_list:
                # t2 is in register
                reg2 = reg2_list[0]
                self.emit(f'cmp {reg2[size]}, {t3}')
            else:
                # t2 is in memory
                address = self.address_map.get_address(t2)
                self.emit(f'cmp {self.size_specifiers[size]} [rbp{address}], {t3}')
        else:
            # Both are variables
            reg2_list = self.reg_allocator.add_desc.get_reg_allocated(t2)
            reg3_list = self.reg_allocator.add_desc.get_reg_allocated(t3)
            
            if reg2_list and reg3_list:
                # Both in registers
                self.emit(f'cmp {reg2_list[0][size]}, {reg3_list[0][size]}')
            elif reg2_list and not reg3_list:
                # t2 in register, t3 in memory
                if t3 in self.address_map.addr_desc:
                    address = self.address_map.get_address(t3)
                    self.emit(f'cmp {reg2_list[0][size]}, {self.size_specifiers[size]} [rbp{address}]')
                else:
                    raise CompileException(f"Variable {t3} not found in memory")
            elif not reg2_list and reg3_list:
                # t2 in memory, t3 in register
                if t2 in self.address_map.addr_desc:
                    address = self.address_map.get_address(t2)
                    self.emit(f'cmp {self.size_specifiers[size]} [rbp{address}], {reg3_list[0][size]}')
                else:
                    raise CompileException(f"Variable {t2} not found in memory")
            else:
                # Both in memory
                addr2 = self.address_map.get_address(t2)
                addr3 = self.address_map.get_address(t3)
                temp_reg = self.reg_allocator.get_register(inst)[0]
                print("+++++++++++++++++++")
                self.emit(f'mov {temp_reg[size]}, {self.size_specifiers[size]} [rbp{addr2}]')
                self.emit(f'cmp {temp_reg[size]}, {self.size_specifiers[size]} [rbp{addr3}]')
        # NOW CMP PART IS DONE , WE NOW ADD THE SETL COMMAND
        #assign new reg for t1
        reg_t1, _ = self.reg_allocator.get_register(inst)
        self.reg_allocator.add_desc.set_entry_to_reg(t1, reg_t1)
        self.reg_allocator.reg_desc.add_var_to_register(reg_t1, t1)
        size = self.get_size_idx(type=type)
        # Clear this reg
        self.emit(f'xor {reg_t1[size]}, {reg_t1[size]}')
        set_instructions = {
        '<': 'setl',
        '<=': 'setle',
        '>': 'setg',
        '>=': 'setge',
        '==': 'sete',
        '!=': 'setne'
        }
        relop = inst.inst[4]
        self.emit(f'{set_instructions[relop]} {reg_t1[3]}')
        #3 because that stores the lower bytes in our reg class
        self.emit(f'movzx {reg_t1[size]}, {reg_t1[3]}')


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
        size = self.size_map.get_size(self.cfg.func_name)
        size = size + ((16-(size)%16) if size%16 != 0 else 0)
        codel4 = f'sub rsp, {size}'
        self.emit(comment)
        self.emit(codel1)
        self.emit(codel2)
        self.emit(codel3)
        self.emit(codel4)
        # params ka kuch karna padega
        for i, param in enumerate(self.param_map.get_params(self.cfg.func_name)):
            param,_ = param
            print(self.size_map)
            print(param)
            size = self.get_size_idx(size=self.size_map.get_size(param))
            address = self.address_map.get_address(param)
            reg = self.param_regs[i]
            codel = f'mov {self.size_specifiers[size]} [rbp{address}], {reg[size]}'
            self.emit(codel)
        
    def handle_end(self, inst):
        label = f'$end{self.cfg.func_name}:'
        codel1 = f'leave'
        codel2 = f'ret'
        self.emit(label)
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
    
    def get_inverse_jump_instruction(self, relop: str) -> str:
        """
        Map relational operator to assembly jump instruction.
        """
        return {
            '<': 'jge',
            '<=': 'jg',
            '>': 'jle',
            '>=': 'jl',
            '==': 'jne',
            '!=': 'je'
        }.get(relop, 'jmp')
    
def driver(filename, graphgen, address_map,size_map,param_map,type_map):
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
        generated_asm.write("global _start\n")
        generated_asm.write("extern printf\n")
        generated_asm.write("extern scanf\n")
        generated_asm.write("extern malloc\n")
        generated_asm.write("extern free\n")
        generated_asm.write("extern exit\n")
        generated_asm.write("; Function _start\n")
        generated_asm.write("_start:\n")
        generated_asm.write("\tand rsp, -16\n")
        generated_asm.write("\tcall main\n")
        generated_asm.write("\tmov rdi, rax\n")
        generated_asm.write("\tcall exit\n")


    for i, cfg in enumerate(cff.cfgs):
        print("In cfg : ", i)
        with open(output_path, 'a') as generated_asm:
            generator = CodeGenerator(cfg,generated_asm,address_map,size_map,param_map,type_map)
            generator.generate_code()
        print("===================================")