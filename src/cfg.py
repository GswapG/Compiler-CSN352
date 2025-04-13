import os
from exceptions import *
from graphviz import Digraph
import re

goto_pattern = r"goto (.+)"
label_to_index = {}

class BasicBlock:
    def __init__(self,id):
        self.block_id = id
        self.instructions = [] # list of instruction strings
        self.successors = [] # list of block ids
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
    
    def __str__(self):
        ret = "block " + str(self.block_id) + '\n'
        for inst in self.instructions:
            ret += inst
            ret += '\n'
        return ret

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
            label_to_index[ret_contents[i][:-1]] = len(res_IR)-1
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
    return contents
        

def assign_leaders(IR):
    """
    Assigns leaders to ir string, returns set of leader indices
    """
    ## Possible cases
    # goto.. (unconditional jump) (where this points to is a leader)
    # if .. (conditional jump) (this is leader, as well as where this points to)
    # .label (function) (this is leader)
    # call .. (function call) (this is leader)
    # <var> = call .. (function call) (this is leader)
    leaders = set()
    n = len(IR)
    if n > 0:
        leaders.add(0)
    branch_pattern = re.compile(r'\bgoto\b\s+(.+)')
    cond_branch_pattern = re.compile(r'\bif\b.*\bgoto\b\s+(.+)')

    for i, line in enumerate(IR):
        m_branch = branch_pattern.search(line)

        if m_branch:
            target_label = m_branch.group(1)
            if target_label in label_to_index:
                print("making target of goto a leader")
                leaders.add(label_to_index[target_label])
            if i + 1 < n:
                if not branch_pattern.search(IR[i+1]):
                    print("making next statement of if goto a label")
                    leaders.add(i+1)
        
        if cond_branch_pattern.search(line):
            print("making if goto a label")
            leaders.add(i)
    return leaders

class CFG:
    def __init__(self,IR,label_to_index):
        self.IR = IR
        self.basic_blocks = [] # list of BasicBlock objects
        self.label_to_index = label_to_index
        self.block_map = {}
        self.curr_id = 0
        self._create_basic_blocks()
        self.construct_graph()
        self.visualize_cfg('cfg')
    
    def add_block(self,block):
        self.basic_blocks.append(block)

    def _create_basic_blocks(self):
        """
        Partition instructions into basic blocks using leader indices.
        """
        leaders = assign_leaders(self.IR)
        leaders = sorted(leaders)
        label_regex = re.compile(r'^.+:')
        curr_block = None
        for i,inst in enumerate(self.IR):
            m_groups = label_regex.search(inst) 
            print(i,inst)
            if m_groups: 
                inst = inst.split(m_groups[0])[1].strip()
            if i in leaders:    
                self.curr_id += 1 
                if curr_block is not None:
                    self.add_block(curr_block)
                curr_block = BasicBlock(self.curr_id)
                curr_block.add_inst(inst)
            else:
                curr_block.add_inst(inst)
            # yahan firse isiliye hai coz upar curr_id might get updated, so cant do this before 
            if m_groups:
                self.block_map[m_groups[0][:-1]] = self.curr_id
        self.add_block(curr_block)

    def print_blocks(self):
        for block in self.basic_blocks:
            print("block number ",block.block_id)
            print(block)
        
    def construct_graph(self):
        branch_pattern = re.compile(r'\bgoto\b\s+(.+)')
        for block in self.basic_blocks:
            for i, inst in enumerate(block.instructions):
                m_blocks = branch_pattern.search(inst)
                # adding jump of goto
                if m_blocks:
                    block.add_successor(self.block_map[m_blocks[1]])
                # if last instruction is not goto, add next block as successor
                if i == (len(block.instructions)-1):
                    # print('at last inst')
                    if not inst.startswith('goto'):
                        block.add_successor(block.block_id+1)
            print(block, block.successors)

    def visualize_cfg(cfg, output_path='cfg'):
        graph = Digraph(comment="Control Flow Graph (Pretty)")
        graph.attr('node', shape='plaintext', fontname='Helvetica')
        graph.attr('edge', arrowhead='vee', arrowsize='0.5')
        graph.attr('graph', rankdir='TB', splines='ortho')

        def escape_html(text):
            if text is None:
                return ""
            return (str(text)
                    .replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;'))

        def format_inst_list(instructions):
            """Return instructions as HTML-style table rows"""
            rows = []
            for inst in instructions:
                escaped = escape_html(inst)
                rows.append(f'<tr><td align="left" port="code"><font face="Courier">{escaped}</font></td></tr>')
            return rows

        # Create a table for each basic block
        for block in cfg.basic_blocks:
            label = ['<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">']
            label.append(f'<tr><td bgcolor="#dce6f1" align="center"><b>Block {block.block_id}</b></td></tr>')
            label.extend(format_inst_list(block.instructions))
            label.append('</table>>')

            graph.node(str(block.block_id), '\n'.join(label))

        # Add edges for successors
        for block in cfg.basic_blocks:
            for succ in block.successors:
                graph.edge(str(block.block_id), str(succ))

        # Render and return
        graph.render(output_path, format='png', cleanup=True)
    
class CFF:
    """
    Takes raw IR and separates all procedures
    For each procedure, it runs cleanup and constructs the cfgs
    Finally visualizes the cfgs 
    """
    def __init__(self,ir_path):
        self.IR = ir_input(ir_path)
        self.cfgs = [] # list of cfg objects

    def separate_procedures(self):
        """
        Separates IR into list of list of instructions belonging to separate procedures 
        Runs cleanup on these separated procedures
        """
        pass

if __name__ == "__main__":
    ir_path = '../generatedIR/ir_test.tac'
    IR = ir_input(ir_path)
    print(label_to_index)
    for i, lin in enumerate(IR):
        print(i,lin)
    cfg = CFG(IR,label_to_index)
    print(cfg.block_map)
    # cfg.print_blocks()