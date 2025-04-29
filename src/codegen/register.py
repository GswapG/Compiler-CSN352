from ..exceptions import *

class Register:
    def __init__(self, id: str, reg_type: str):
        """
        id: base name of register (e.g., 'rax', 'rbx', etc.)
        reg_type: 'int' or 'float'
        """
        self.id = id  # e.g., 'rax'
        self.type = reg_type  # 'int' or 'float'

        # Internal tracking for allocation
        self.variable = None
        self.in_use = False
        self.dirty = False
        self.last_used = -1

        # Name mappings for subregisters [64, 32, 16, 8l, 8h]
        self.variants = self.build_variant_names(id)
        # Calling convention
        self.caller_saved = False
        self.callee_saved = False

    def build_variant_names(self, id: str):
        mapping = {
            'rax': ['rax', 'eax', 'ax', 'al', 'ah'],
            'rbx': ['rbx', 'ebx', 'bx', 'bl', 'bh'],
            'rcx': ['rcx', 'ecx', 'cx', 'cl', 'ch'],
            'rdx': ['rdx', 'edx', 'dx', 'dl', 'dh'],
            'rsi': ['rsi', 'esi', 'si', 'sil', None],
            'rdi': ['rdi', 'edi', 'di', 'dil', None],
            'rbp': ['rbp', 'ebp', 'bp', 'bpl', None],
            'rsp': ['rsp', 'esp', 'sp', 'spl', None],
            'r8':  ['r8', 'r8d', 'r8w', 'r8b', None],
            'r9':  ['r9', 'r9d', 'r9w', 'r9b', None],
            'r10':  ['r10', 'r10d', 'r10w', 'r10b', None],
            'r11':  ['r11', 'r11d', 'r11w', 'r11b', None],
            'r12':  ['r12', 'r12d', 'r12w', 'r12b', None],
            'r13':  ['r13', 'r13d', 'r13w', 'r13b', None],
            'r14':  ['r14', 'r14d', 'r14w', 'r14b', None],
            'r15':  ['r15', 'r15d', 'r15w', 'r15b', None]
        }
        return mapping.get(id, [id]*5)

    def __getitem__(self, idx):
        """
        Index meanings:
        [0] = 64-bit
        [1] = 32-bit
        [2] = 16-bit
        [3] = 8-bit low
        [4] = 8-bit high (only for some)
        """
        if idx > 4 or self.variants[idx] is None:
            raise IndexError(f"{self.id} does not support index {idx}")
        return self.variants[idx]

    def __str__(self):
        return self[0]  # default 64-bit for display


def init_gpr() -> list[Register]:
    reg_names = [
        'rax', 'rbx', 'rcx', 'rdx',
        'rsi', 'rdi',
        'r8', 'r9', 'r10', 'r11',
        'r12', 'r13', 'r14', 'r15'
    ]

    # Define caller- and callee-saved sets
    caller_saved = {'rax', 'rcx', 'rdx', 'rsi', 'rdi', 'r8', 'r9', 'r10', 'r11'}
    callee_saved = {'rbx', 'r12', 'r13', 'r14', 'r15'}

    registers = []
    for name in reg_names:
        reg = Register(name, 'int')
        reg.caller_saved = name in caller_saved
        reg.callee_saved = name in callee_saved
        registers.append(reg)

    return registers


def init_param_registers() -> list[Register]:
	"""
	Initializes registers rdi, rsi, rdx, rcx, r8, and r9 and returns them in a list.
	"""
	reg_names = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
	registers = [Register(name, 'int') for name in reg_names]
	return registers

