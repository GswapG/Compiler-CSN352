import os
from exceptions import *
import re

goto_pattern = r"goto (\$L\d+)"

class BasicBlock:
    def __init__(self):
        self.block_id = None
        self.instructions = ""
        self.successors = []
        self.parent = None

    def add_inst(self, inst):
        """
        Self explainatory
        """
        self.instructions.append(inst)

    def add_successor(self, succ):
        """
        Self Explainatory
        """
        self.successors.append(succ)

def ir_cleanup(IR):
    """
    1. Removes trailing and leading spaces from each line
    2. Merges labels pointing to same instruction (makes necessary changes to IR)
    3. Flattens labels to next line (currently label pointing to line n is present at line n-1)
    """
    ret_contents = []
    _labels = {}
    curr_labels = []
    for i, line in enumerate(IR):
        line = line.strip()
        if line[0] == '$':
            label = ""
            i = 0; 
            while(line[i]!=':'):
                label += line[i]
                i += 1
            curr_labels.append(label)
        else:
            if len(curr_labels) != 0:
                for label in curr_labels:
                    _labels[label] = curr_labels[0]
            curr_labels = []       
        if len(curr_labels) <= 1:
            ret_contents.append(line)

    for i, line in enumerate(ret_contents):
        def replace_match(match):
            label = match.group(1)
            return f"goto {_labels.get(label,label)}"
        line = re.sub(goto_pattern,replace_match, line)
        ret_contents[i] = line


    i = 0
    res_IR = []
    while(i<(len(ret_contents)-1)):
        if ret_contents[i][0] == '$' or ret_contents[i][0] == '.':
            # general label
            res_IR.append(ret_contents[i] + " " + ret_contents[i+1])
            i += 1
        else:
            res_IR.append(ret_contents[i])
        i += 1
    return res_IR


def ir_input(ir_path):
    """
    Takes input, validates it and processes it for cfg generation
    """
    if not os.path.exists(ir_path):
        raise CompileFileNotFound(f"File specified at : {ir_path} was not found (does not exist?)")
    if not ir_path.endswith('.tac'):
        raise CompileException("Wrong IR Format!!")
    
    contents = None

    with open(ir_path,"r") as file:
        contents = file.readlines()

    return ir_cleanup(contents)
        

def assign_leaders(IR):
    """
    Assigns leaders to ir string (appends %$% to end of line)
    """
    ## Possible cases
    # goto.. (unconditional jump) (this is leader, as well as where this points to)
    # if .. (conditional jump) (this is leader, as well as where this points to)
    # .label (function) (this is leader)
    # call .. (function call) (this is leader)
    # <var> = call .. (function call) (this is leader)
    for line in IR:
        pass

def construct_cfg():
    """
    Constructs the cfg using leader-assigned IR and returns the root pointer 
    """
    pass

if __name__ == "__main__":
    ir_path = '../generatedIR/ir_test.tac'
    for lin in ir_input(ir_path):
        print(lin)