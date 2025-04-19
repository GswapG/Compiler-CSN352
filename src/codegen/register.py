from ..exceptions import *

class Register:
    def __init__(self,id,Type):
        """
        [0]->64(RX)
        [1]->32(EX)
        [2]->16(X)
        [3]->8(L)
        [4]->8(H)
        self.type -> int or float (rax or xmm)
        """
        self.id = id
        self.type = Type
    
    def __getitem__(self,idx):
        if idx > 4:
            raise CompileException(f"Can't index this register at index : {idx}")

        