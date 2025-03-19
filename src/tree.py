from graphviz import Digraph
from collections import deque
# AST
symbol_table = []
abcd=0

class Node:
    def __init__(self, type, children = None): 
        global abcd
        self.type = type
        self.name = str(abcd)
        abcd+=1
        print(abcd)
        self.children = []
        self.vars = []
        self.dtypes = []
        self.pointer_count = 0
        self.is_const = 0
        if children:
            children_conv = []
            for c in children:
                if not isinstance(c,Node):
                    children_conv.append(Node(str(c)))
                else:
                    children_conv.append(c)        
            self.children = children_conv
        for c in self.children:
            if isinstance(c,Node):
                self.vars += c.vars
                self.dtypes += c.dtypes
                self.pointer_count += c.pointer_count
                self.is_const |= c.is_const
                # c.dtypes.clear()
                # c.vars.clear()
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


