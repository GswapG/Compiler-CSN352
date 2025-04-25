from .add_desc import *
from .reg_desc import *
from .codegenerator import *

class RegisterAllocator:
    """
    Takes in entire tac instruction 
    Gives out available registers for operands
    Updates Register and Address Descriptors
    """
    def __init__(self, registers: list[Register], code_generator: "CodeGenerator"):
        """
        Create address and register descriptor
        """
        self.add_desc = AddressDescriptor()
        self.reg_desc = RegisterDescriptor(registers)
        self.code_generator = code_generator
        self.regs_on_stack = [] #list of caller saved registers stored on stack (before function call)

    def set_next_use(self, use: defaultdict):
        self.next_use = use
    
    def get_register(self, inst: "Instruction") -> list[Register]:
        """
        Parse the inst (tac) to find what variables need registers.
        Returns a list of registers (memory locations)
        """
        ret = []
        if inst.is_assignment:
            if inst.is_function_call:
                # t = call func, n
                pass
            elif inst.is_operation:
                # t1 = t2 op t3
                t1 = inst.inst[0]
                t2 = inst.inst[2]
                t3 = inst.inst[5]
                op = inst.inst[4]
                print(t1,t2,t3,op)
                # finding R1
                r = self.add_desc.get_reg_allocated(t2)
                if r:
                    # register exists for t2
                    ret.append(r[0])
                else:
                    # load into a free register
                    ## NEED TO ADD A LOAD INSTRUCTION HERE
                    r = self.reg_desc.get_free_register()
                    if r:
                        ret.append(r)
                    else:
                        # need to spill some register
                        # TODO
                        pass
                # finding R2
                r = self.add_desc.get_reg_allocated(t3)
                if r:
                    # reg exists for t3
                    ret.append(r[0])
                else:
                    # load into free register
                    ## NEED TO ADD A LOAD INSTRUCTION HERE
                    r = self.reg_desc.get_free_register()
                    if r:
                        ret.append(r)
                    else:
                        # need to spill some register
                        # TODO
                        pass
            elif inst.is_cast:
                # t1 = cast t2
                pass
            else:
                # t1 = t2
                pass
        return ret
    
    def spill_selector(self,uses: defaultdict):
        """
        Selects register to spill based on heuristic (least uses)
        Spills the selected register
        Emits required instructions using self.code_generator
        Returns the selected register
        """
        pass

    def spill(self, var: str) -> Register:
        """
        Spills register corresponding to given var.
        Updates descriptors accordingly
        """
        regs = self.add_desc.get_reg_allocated(var)
        if regs is None:
            raise CompileException(f"No register contains var, yet an attempt was made to spill it")
        
        reg = regs[0]
        self.reg_desc.clear_register(reg)
        self.add_desc.discard_reg_for_var(var, reg)
        return reg
    
    def store_all(self):
        """
        To be called at the end of a block to store all variables in memory and free all registers.
        """
        pass

    def push_regs_to_stack(self):
        """
        Called before function call.
        Any caller saved register in use will be stored onto the stack.
        """
        pass
    
    def pop_regs_from_stack(self):
        """
        Called after function call to restore state of caller saved registers.
        """
        pass