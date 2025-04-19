import os
from ..exceptions import *
from graphviz import Digraph
import re
print(__package__)
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


def ir_input(ir_path:str)->list:
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
    print(type(contents))
    return contents
        

class CFG:
    def __init__(self,IR):
        self.IR = IR
        self.basic_blocks = [] # list of BasicBlock objects
        self.block_map = {}
        self.curr_id = 0
        self.label_to_index = {}
        self.ir_cleanup()
        self._create_basic_blocks()
        self.construct_graph()
    
    def add_block(self,block):
        self.basic_blocks.append(block)

    def ir_cleanup(self):
        """
        1. Removes trailing and leading spaces from each line
        2. Merges labels pointing to same instruction (makes necessary changes to IR)
        3. Flattens labels to next line (currently label pointing to line n is present at line n-1)
        """
        ret_contents = []
        _labels = {}
        curr_labels = []
        goto_pattern = r"goto (.+)"
        print(self.IR)
        for i, line in enumerate(self.IR):
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
                self.label_to_index[ret_contents[i][:-1]] = len(res_IR)-1
                i += 1
            else:
                res_IR.append(ret_contents[i])
            i += 1
        if(i < len(ret_contents)):
            res_IR.append(ret_contents[i])
        
        self.IR = res_IR
    
    def assign_leaders(self):
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
        n = len(self.IR)
        if n > 0:
            leaders.add(0)
        branch_pattern = re.compile(r'\bgoto\b\s+(.+)')
        cond_branch_pattern = re.compile(r'\bif\b.*\bgoto\b\s+(.+)')
        print(self.IR)
        for i, line in enumerate(self.IR):
            m_branch = branch_pattern.search(line)

            if m_branch:
                target_label = m_branch.group(1)
                if target_label in self.label_to_index:
                    print("making target of goto a leader")
                    leaders.add(self.label_to_index[target_label])
                if i + 1 < n:
                    if not branch_pattern.search(self.IR[i+1]):
                        print("making next statement of goto a leader")
                        leaders.add(i+1)
            
            if cond_branch_pattern.search(line):
                print("making if goto a leader")
                leaders.add(i)
        return leaders

    def _create_basic_blocks(self):
        """
        Partition instructions into basic blocks using leader indices.
        """
        leaders = self.assign_leaders()
        leaders = sorted(leaders)
        print(leaders)
        label_regex = re.compile(r'^.+:')
        curr_block = None
        for i,inst in enumerate(self.IR):
            print("PARSING INSTR: ", inst)
            m_groups = label_regex.search(inst) 
            print(i,inst)
            if m_groups: 
                inst = inst.split(m_groups[0])[1].strip()
            if i in leaders:    
                self.curr_id += 1 
                if curr_block is not None:
                    self.add_block(curr_block)
                curr_block = BasicBlock(self.curr_id)
                if inst.strip():  # skip if instruction is empty
                    print("ADDING INSTR: ", inst)
                    curr_block.add_inst(inst)
            else:
                if inst.strip():  # skip if instruction is empty
                    print("ADDING INSTR: ", inst)
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
        for block_idx, block in enumerate(self.basic_blocks):
            for i, inst in enumerate(block.instructions):
                m_blocks = branch_pattern.search(inst)
                # adding jump of goto
                if m_blocks:
                    block.add_successor(self.block_map[m_blocks[1]])
                # if last instruction is not goto, add next block as successor
                if i == (len(block.instructions)-1):
                    # print('at last inst')
                    if (not inst.startswith('goto')) and (block_idx < (len(self.basic_blocks)-1)):
                        block.add_successor(block.block_id+1)
            print(block, block.successors)

    def visualize_cfg(self, graph=None, cluster_name=None):
        new_graph = False
        if graph is None:
            graph = Digraph(comment="Control Flow Graph")
            graph.attr('graph', rankdir='TB', splines='true')
            graph.attr('node', shape='plaintext', fontname='Helvetica')
            graph.attr('edge', arrowhead='vee', arrowsize='0.5')
            new_graph = True

        def escape_html(text):
            if text is None:
                return ""
            return (str(text)
                    .replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;'))

        def format_inst_list(instructions):
            rows = []
            for inst in instructions:
                escaped = escape_html(inst)
                rows.append(f'<tr><td align="left" port="code"><font face="Courier">{escaped}</font></td></tr>')
            return rows

        if cluster_name:
            with graph.subgraph(name=f'cluster_{cluster_name}') as sub:
                sub.attr(label=f'Function: {cluster_name}', style='filled', color='lightgrey', fontname='Helvetica')

                for block in self.basic_blocks:
                    label = ['<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">']
                    header_style = 'bgcolor="#dce6f1"'

                    # Check if it's the last block in the function
                    is_last = (block == self.basic_blocks[-1])
                    if is_last:
                        header_style = 'bgcolor="#fdd9d9"'  # Light red with dark text

                    label.append(f'<tr><td {header_style} align="center"><b>Block {block.block_id}</b></td></tr>')
                    label.extend(format_inst_list(block.instructions))
                    label.append('</table>>')

                    node_id = f"{cluster_name}_b{block.block_id}"
                    sub.node(node_id, '\n'.join(label))


                for block in self.basic_blocks:
                    for succ in block.successors:
                        last_inst = block.instructions[-1] if block.instructions else ""
                        style = 'solid'
                        color = 'black'
                        if last_inst.startswith("if"):
                            color = 'blue'
                        elif last_inst.startswith("goto"):
                            color = 'darkgreen'

                        from_node = f"{cluster_name}_b{block.block_id}"
                        to_node = f"{cluster_name}_b{succ}"
                        sub.edge(from_node, to_node, color=color, style=style)

        else:
            for block in self.basic_blocks:
                label = ['<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">']
                header_style = 'bgcolor="#dce6f1"'

                # Check if it's the last block in the function
                is_last = (block == self.basic_blocks[-1])
                if is_last:
                    header_style = 'bgcolor="#fdd9d9"'  # Light red with dark text

                label.append(f'<tr><td {header_style} align="center"><b>Block {block.block_id}</b></td></tr>')
                label.extend(format_inst_list(block.instructions))
                label.append('</table>>')

                node_id = f"{cluster_name}_b{block.block_id}"
                graph.node(node_id, '\n'.join(label))

            for block in self.basic_blocks:
                for succ in block.successors:
                    last_inst = block.instructions[-1] if block.instructions else ""
                    style = 'solid'
                    color = 'black'
                    if last_inst.startswith("if"):
                        color = 'blue'
                    elif last_inst.startswith("goto"):
                        color = 'darkgreen'

                    from_node = f"{cluster_name}_b{block.block_id}"
                    to_node = f"{cluster_name}_b{succ}"
                    graph.edge(from_node, to_node, color=color, style=style)

        if new_graph:
            graph.render('cfg', format='png', cleanup=True)

        return graph


    
class CFF:
    """
    Takes raw IR and separates all procedures
    For each procedure, it runs cleanup and constructs the cfgs
    Finally visualizes the cfgs 
    """
    def __init__(self,IR):
        self.IR = IR
        self.func_irs = [] # list of separated IRs
        self.func_names = []
        self.global_ir = [] 
        self.cfgs = [] # list of cfg objects
        self._separate_procedures()
        self.print_irs()
        print(self.func_names)
        print(self.global_ir)
        self._construct_graphs()

    def _separate_procedures(self):
        """
        Separates IR into list of instructions belonging to each procedure.
        Also handles global instructions outside any function.
        """
        curr = []
        inside_func = False

        for i, line in enumerate(self.IR):
            if "BeginFunc" in line:
                self.func_names.append(self.IR[i-1].strip()[1:-1])
                inside_func = True
                curr = [line]  
            elif "EndFunc" in line:
                curr.append(line)
                self.func_irs.append(curr)
                curr = []
                inside_func = False
            else:
                if inside_func:
                    curr.append(line)
                else:
                    self.global_ir.append(line)

    
    def _construct_graphs(self):
        """
        Constructs graphs for separated procedures
        """
        if self.global_ir:
            self.cfgs.append(CFG(self.global_ir))
        for ir in self.func_irs:
            self.cfgs.append(CFG(ir))

    def print_irs(self):
        """
        Helper to print separated irs for debugging
        """
        for j,ir in enumerate(self.func_irs):
            print(f"Ir {j}")
            for i, line in enumerate(ir):
                print(i, line)
        
    def visualize_all_cfgs(self, output_path='combined_cfg'):
        graph = Digraph(comment="All Function CFGs")
        graph.attr('graph', rankdir='TB', splines='ortho') 
        graph.attr('node', shape='plaintext', fontname='Helvetica')
        graph.attr('edge', arrowhead='vee', arrowsize='0.5')

        for i, cfg in enumerate(self.cfgs):
            if self.global_ir and i == 0:
                func_name = 'global'
            else:
                func_name = self.func_names[i-1] if self.global_ir else self.func_names[i]

            cfg.visualize_cfg(graph=graph, cluster_name=func_name)

        graph.render(output_path, format='png', cleanup=True)


if __name__ == "__main__":
    ir_path = './generatedIR/ir_test.tac'
    IR = ir_input(ir_path)
    cff = CFF(IR)
    cff.visualize_all_cfgs('./generatedCFG/ir_test.tac')
    # cfg.print_blocks()