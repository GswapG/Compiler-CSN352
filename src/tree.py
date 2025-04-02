from graphviz import Digraph
from collections import deque
from .ir import IR
import copy
# AST
symbol_table = []
node_name = 0

class Node:
    def __init__(self, type, children = None): 
        global node_name
        self.type = type
        self.name = ""
        self.children = []
        self.vars = []
        self.dtypes = []
        self.fdtypes = []
        self.rhs = []
        self.is_const = 0
        self.is_address = False
        self.isbraces = False
        self.return_type = None
        self.iscall = 0
        self.param_list = []
        self.operator = None
        self.lvalue = None
        self.rvalue = None
        self.listup = []
        self.ir = IR()
        self.expression = ""
        self.break_count = False
        self.continue_count = False
        self.default_count = 0

        if children is None:    
            self.expression += type
        else:
            children_conv = []
            for c in children:
                if not isinstance(c,Node):
                    children_conv.append(Node(str(c)))
                else:
                    children_conv.append(c)
            self.children = children_conv

        if len(self.children) == 1 and isinstance(self.children[0], Node):
            self.return_type = self.children[0].return_type
            self.iscall = self.children[0].iscall
            self.lvalue = self.children[0].lvalue
            self.rvalue = self.children[0].rvalue
            self.name = self.children[0].name
            self.ir = copy.deepcopy(self.children[0].ir)

        for c in self.children:
            self.is_address |= c.is_address
            self.isbraces |= c.isbraces
            self.break_count |= c.break_count
            self.continue_count |= c.continue_count
            self.default_count += c.default_count

            if isinstance(c, Node):
                self.expression += c.expression
                self.vars += c.vars
                self.dtypes += c.dtypes
                self.fdtypes += c.fdtypes
                self.rhs += c.rhs
                self.is_const |= c.is_const

    def __repr__(self):
        return f"Node({self.type})"

    def to_graph(self, graph=None):
        if graph is None:
            graph = Digraph()
            graph.node(str(id(self)), label=self.type)
        
        for child in self.children:
            if isinstance(child, Node):
                graph.node(str(id(child)), label=child.type)
                graph.edge(str(id(self)), str(id(child)))
                child.to_graph(graph)
            # else:
            #     child_id = f"{id(self)}_{id(child)}"
            #     graph.node(child_id, label=str(child))
            #     graph.edge(str(id(self)), child_id)
        
        return graph
    
    def to_annotated_parse_tree(self, graph=None):
        if graph is None:
            graph = Digraph()
            graph.attr('node', shape='plaintext', margin='0.2', fontname='Helvetica')
            graph.attr('edge', arrowhead='vee', arrowsize='0.5')
            graph.attr('graph', rankdir='TB', splines='ortho')

        def escape_html(text):
            """Escape only HTML-sensitive characters (single pass)"""
            if text is None:
                return ""
            return (str(text)
                    .replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;'))

        def format_code(code):
            """Format code with proper escaping and line breaks"""
            if not code:
                return ""
            # First escape HTML, then handle whitespace
            return (escape_html(code)
                    .replace('\n', '<BR ALIGN="LEFT"/>')
                    .replace('\t', '    '))  # 4 spaces for tabs

        # Create HTML-like table for the node
        node_label = ['<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">']
        
        # Node type header
        node_label.append(f'<tr><td bgcolor="#f0f0f0" align="center"><b>{escape_html(self.type)}</b></td></tr>')
        
        # Process IR attributes
        if self.ir and any([self.ir.place, self.ir.code]):
            ir_info = []
            
            # Generic attribute formatter
            def format_attr(value):
                if isinstance(value, list):
                    return ', '.join(escape_html(str(v)) for v in value)
                return escape_html(str(value))

            # Special handling for code
            if self.ir.code:
                code_content = format_code(self.ir.code)
                ir_info.append(('code', f'<font face="Courier">{code_content}</font>'))

            # Add other attributes
            attrs = [
                ('place', self.ir.place),
                ('truelist', self.ir.truelist),
                ('falselist', self.ir.falselist),
                ('nextlist', self.ir.nextlist),
                ('begin', self.ir.begin),
                ('after', self.ir.after),
                ('params', self.ir.parameters),
                ('else', self.ir.else_),
                ('initializer_list', self.ir.initializer_list)
            ]
            
            for name, value in attrs:
                if value:
                    ir_info.append((name, format_attr(value)))

            # Build table rows
            for name, value in ir_info:
                node_label.append(f'<tr><td align="left"><i>{escape_html(name)}:</i> {value}</td></tr>')

        node_label.append('</table>>')
        
        # Create node with properly escaped label
        graph.node(str(id(self)), label='\n'.join(node_label))

        # Process children
        for child in self.children:
            if isinstance(child, Node):
                child_label = [
                    '<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">',
                    f'<tr><td align="center" bgcolor="#f0f0f0">{escape_html(child.type)}</td></tr>',
                    '</table>>'
                ]
                graph.node(str(id(child)), label='\n'.join(child_label))
                graph.edge(str(id(self)), str(id(child)))
                child.to_annotated_parse_tree(graph)

        return graph
    
    def dfs2(self):
        """if one parent and one child then both get linked and i disappear"""
        for i in range(len(self.children)):
            while len(self.children[i].children) == 1:
                self.children[i] = self.children[i].children[0]
        for child in self.children:
            child.dfs2()


    
def dfs(node, indent=0):
    """Recursively prints the AST."""
    # Check if the node is a string or a Node object
    if isinstance(node, Node):
        # Print the current node's type
        print(" " * indent + f"Node: {node.type}")
        
        # Recursively print each child
        for child in node.children:
            dfs(child, indent + 4)
    else:
        print(node)
      
def level_order(node):
    queue = deque()
    queue.append(node)
    while(queue):
        sz = len(queue)
        for i in range(0,sz):
            v = queue.popleft()
            if isinstance(v,Node):
                print(f"Node: {v.type}",end=" ")
                for u in v.children:
                    queue.append(u)
            else:
                print(f"Value: {v}",end = " ")
        print("\n \n")


