from collections import defaultdict, deque
from graphviz import Digraph

def strict_equal(a, b):
    return type(a) is type(b) and a == b

class SymbolEntry:
    def __init__(self, name, type, kind, child=None, node=None, isForwardable=False,refsto = None):
        """
            name        -> identifier
            type        -> data type
            kind        -> variable/function/etc
            scope_level -> scope tree depth
            scope_name  -> scope name 
        """

        self.name = name
        self.type = type
        self.kind = kind
        self.node = node
        self.child = child
        self.isForwardable = isForwardable
        self.refsto = refsto

class SymbolEntryNode:
    def __init__(self, scope_level, scope_name, parent=None):
        """
            maintain a list of entries in a node
            a node in the symbol tree should maintain its immediate parent and its children scopes
            traversing parent tree could reveal it's scope_level and scope_name. 
            all the entries in a node should have the same scope_level and scope_name
        """

        self.parent = parent
        self.children = []
        self.entries = []
        self.scope_level = scope_level
        self.scope_name = scope_name

    def add_entry(self, entry):
        if not isinstance(entry, SymbolEntry):
            raise ValueError("Incorrect Use of add_entry method")
        
        self.entries.append(entry)

    def to_graph(self, graph=None):
        """Recursively generate Graphviz representation of the symbol tree"""
        if graph is None:
            graph = Digraph()
            graph.attr('node', shape='plaintext', margin='0')
        
        # Create HTML table label for this scope node
        label = [
            '<<table border="1" cellborder="0" cellspacing="0">',
            f'<tr><td colspan="3"><b>{self.scope_name}</b><br/>(Level {self.scope_level})</td></tr>'
        ]
        
        # Add symbol entries as table rows
        for entry in self.entries:
            label.append(
                f'<tr><td>{entry.name}</td><td>{entry.type}</td><td>{entry.kind}</td></tr>'
            )
        label.append('</table>>')
        
        # Add node to graph
        graph.node(str(id(self)), ''.join(label))
        
        # Recursively add child scopes
        for child in self.children:
            child.to_graph(graph)
            graph.edge(str(id(self)), str(id(child)))
        
        return graph

class SymbolTableEntry:
    def __init__(self, name, type, kind, entry, node, scope, scope_name,refers_to = None):
        self.name = name 
        self.type = type 
        self.kind = kind 
        self.entry = entry
        self.node = node
        self.scope = scope
        self.scope_name = scope_name
        self.refers_to = refers_to

class SymbolTable:
    def __init__(self):
        self.root = SymbolEntryNode(0, "global")
        self.current_scope = self.root 
        self.current_scope_name = self.root.scope_name
        self.current_scope_level = self.root.scope_level
        self.table_entries = []

        self.to_add_child = False
        self.the_child = None

        self.to_add_parent = False
        self.the_parent = None

    def clear(self):
        self.root = SymbolEntryNode(0, "global")
        self.current_scope = self.root 
        self.current_scope_name = self.root.scope_name
        self.current_scope_level = self.root.scope_level
        self.table_entries = []

    def enter_scope(self):
        self.current_scope_level += 1
        self.current_scope_name = f"block@{self.current_scope_level}"
        scope_node = SymbolEntryNode(self.current_scope_level, self.current_scope_name, self.current_scope)

        if self.to_add_parent:
            self.to_add_parent = False
            self.the_parent.child = scope_node
            self.the_parent = None

        forward_entries = []
        for entry in scope_node.parent.entries:
            if entry.isForwardable:
                forward_entries.append(entry)
                entry.node = scope_node
                entry.isForwardable = False
                scope_node.entries.append(entry)

                # Add to table_entries if not forwardable anymore
                entry = SymbolTableEntry(entry.name, entry.type, entry.kind, entry, entry.node, entry.node.scope_level, entry.node.scope_name)
                self.table_entries.append(entry)

        # Correctly update parent's entries by filtering out forwarded entries
        scope_node.parent.entries = [entry for entry in scope_node.parent.entries if entry not in forward_entries]

        self.current_scope.children.append(scope_node)
        self.current_scope = scope_node

    def exit_scope(self):
        """
            to exit the scope, dont pop the mess just traverse to the parent back 
        """

        self.to_add_child = True
        self.the_child = self.current_scope

        parent = self.current_scope.parent 

        self.current_scope_name = parent.scope_name
        self.current_scope_level = parent.scope_level 
        self.current_scope = parent 

    def link_symbol(self, symbol):
        if not isinstance(symbol, SymbolEntry):
            raise ValueError("Incorrect type of object")
        
        found = False
        present_symbol = None

        for entry in self.current_scope.entries:
            if strict_equal(entry.name, symbol.name):
                if entry.kind != "constant":
                    found = True

                    if self.to_add_child:
                        self.to_add_child = False
                        entry.child = self.the_child
                        self.the_child = None 

                    break 
        
        if not found:
            raise Exception("this symbol entry doesnt exist, cant link it up")


    def add_symbol(self, symbol):
        """
            add the symbol object to the current scope
        """

        if not isinstance(symbol, SymbolEntry):
            raise ValueError("Incorrect type of object")

        for entry in self.current_scope.entries:
            if strict_equal(entry.name, symbol.name):
                # print(entry.type)
                if entry.kind != "constant":
                    raise ValueError(f"Duplicate symbol '{symbol.name}' in scope {self.current_scope_name}")
                else:
                    return
        
        if self.to_add_child:
            self.to_add_child = False
            symbol.child = self.the_child
            self.the_child = None 

        sym2 = symbol
        if isinstance(sym2.name,str) and sym2.name[-1] == '$':
            c = 0
            while sym2.name[-1] == '$':
                c+=1
                sym2.name = sym2.name[:-1]
            sym2.type = c*'*' + sym2.type
        sym2.node = self.current_scope
        self.current_scope.entries.append(sym2)

        if not symbol.isForwardable:
            c = 0
            if not isinstance(symbol.name,str) or  symbol.name[-1] != '$':
                entry = SymbolTableEntry(symbol.name, symbol.type, symbol.kind, symbol, symbol.node, self.current_scope_level, self.current_scope_name)
                self.table_entries.append(entry)
            else:
                while symbol.name[-1] == '$':
                    symbol.name = symbol.name[:-1]
                    c+=1
                # print(symbol.name)
                entry = SymbolTableEntry(symbol.name, c* '*' + symbol.type, symbol.kind, symbol, symbol.node, self.current_scope_level, self.current_scope_name,symbol.refsto)
                self.table_entries.append(entry)

        print("added symbol",symbol.name)
        
    def lookup(self, name):
        scope_pointer = self.current_scope
        while scope_pointer:
            for entry in scope_pointer.entries:
                if strict_equal(entry.name, name):
                    return entry
            scope_pointer = scope_pointer.parent
        return None
    
    def search_params(self, name):
        func_entry = None
        for entry in self.table_entries:
            if entry.name == name:
                func_entry = entry.entry
                break
    
        if func_entry is None:
            raise Exception(f"identifier {name} doesnt exist.")
        
        child_scope = func_entry.child
        params = []
        for entry in child_scope.entries:
            if entry.kind == "parameter":
                params.append(entry)

        return params
    
    def search_struct(self, name, identifier):
        scope_pointer = self.current_scope

        found_struct = None
        found = False
        while scope_pointer:
            for entry in scope_pointer.entries:
                if strict_equal(entry.name, name):
                    found = True
                    found_struct = entry
                    break
            if found:
                break
            scope_pointer = scope_pointer.parent

        if not found:
            return None
        
        struct_scope = entry.child
        for entry in struct_scope.entries:
            if strict_equal(entry.name, identifier):
                return entry
        
        return None

    def __str__(self):
        """
            print the symbol table object
        """

        headers = ["Name", "Type", "Kind", "Scope", "ScopeName"]
        rows = []

        for entry in self.table_entries:
            rows.append([
                entry.name, entry.type, entry.kind, entry.scope, entry.scope_name
            ])

        return tabulate(rows, headers=headers, tablefmt="grid")
    
    def to_graph(self):
        """Entry point for generating the graph"""
        return self.root.to_graph()

try:
    from tabulate import tabulate

except ImportError:
    print("Install tabulate for better output: pip install tabulate")
    def tabulate(*args, **kwargs):
        return str(args[0])
         
symtab = SymbolTable()
