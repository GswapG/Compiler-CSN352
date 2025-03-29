from collections import defaultdict, deque
from graphviz import Digraph
from .utils import *

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
        self.isFunctionDefinition = False

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

        self.function_definition = False
        self.function_scope = None
        self.function_symbol = None

        self.parameters = []

    def clear(self):
        self.root = SymbolEntryNode(0, "global")
        self.current_scope = self.root 
        self.current_scope_name = self.root.scope_name
        self.current_scope_level = self.root.scope_level
        self.table_entries = []

    def function_enter_scope(self):
        self.current_scope_level += 1
        self.current_scope_name = f"block@{self.current_scope_level}"

        if not self.function_definition:
            scope_node = SymbolEntryNode(self.current_scope_level, self.current_scope_name, self.current_scope)
            self.current_scope.children.append(scope_node)

        else:
            scope_node = self.function_scope
            
            if not self.function_symbol.isFunctionDefinition:
                raise Exception(f"Function {self.function_symbol.name} has been already defined")
            
            self.function_symbol.isFunctionDefinition = False
            self.function_definition = False
            self.function_scope = None
            self.function_symbol = None

        self.current_scope = scope_node

    def enter_scope(self):
        self.current_scope_level += 1
        self.current_scope_name = f"block@{self.current_scope_level}"

        if self.function_definition:
            self.function_definition = False
            self.function_scope = None
            self.function_symbol = None

        if not self.function_definition:
            scope_node = SymbolEntryNode(self.current_scope_level, self.current_scope_name, self.current_scope)
            self.current_scope.children.append(scope_node)

        else:
            scope_node = self.function_scope
            
            if not self.function_symbol.isFunctionDefinition:
                raise Exception(f"Function {self.function_symbol.name} has been already defined")
            
            self.function_symbol.isFunctionDefinition = False
            self.function_definition = False
            self.function_scope = None
            self.function_symbol = None

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

    def function_exit_scope(self):
        parent = self.current_scope.parent 
        self.current_scope_name = parent.scope_name
        self.current_scope_level = parent.scope_level 
        self.current_scope = parent 

    def add_function_symbol(self, symbol):
        if not isinstance(symbol, SymbolEntry):
            raise ValueError("Incorrect type of object")
        
        if isinstance(symbol.name, str) and symbol.name[-1] == '$':
            c = 0
            while symbol.name[-1] == '$':
                c+=1
                symbol.name = symbol.name[:-1]
            symbol.type = c*'*' + symbol.type
        
        if symbol.kind != "function":
            if "void" in (symbol.type).split(" "):
                raise ValueError("void type is not allowed for variables")
        
        isDefinition = False
        definitionScope = None
        definitionSymbol = None

        for entry in self.current_scope.entries:
            if strict_equal(entry.name, symbol.name):
                if entry.kind != "constant":
                    if entry.kind == "function":
                        if not entry.isFunctionDefinition:
                            raise ValueError(f"Duplicate symbol '{symbol.name}' in scope {self.current_scope_name}")
                        else:
                            isDefinition = True
                            definitionSymbol = entry 
                            definitionScope = entry.child
                            break
                    else:
                        raise ValueError(f"Duplicate symbol '{symbol.name}' in scope {self.current_scope_name}")

                else:
                    return

        symbol.node = self.current_scope
        symbol.isFunctionDefinition = True
        
        child_scope = SymbolEntryNode(self.current_scope_level + 1, f"block@{self.current_scope_level + 1}", self.current_scope)
        symbol.child = child_scope

        if not isDefinition:
            c = 0
            if not isinstance(symbol.name,str) or  symbol.name[-1] != '$':
                entry = SymbolTableEntry(symbol.name, symbol.type, symbol.kind, symbol, symbol.node, self.current_scope_level, self.current_scope_name)
                self.table_entries.append(entry)
            else:
                while symbol.name[-1] == '$':
                    symbol.name = symbol.name[:-1]
                    c += 1
                entry = SymbolTableEntry(symbol.name, c * '*' + symbol.type, symbol.kind, symbol, symbol.node, self.current_scope_level, self.current_scope_name,symbol.refsto)
                self.table_entries.append(entry)

            for entry in self.parameters:
                new_entry = entry
                new_entry.node = child_scope
                new_entry.isForwardable = False
                
                child_scope.entries.append(new_entry)

                # Add to table_entries if not forwardable anymore
                new_entry = SymbolTableEntry(new_entry.name, new_entry.type, new_entry.kind, new_entry, new_entry.node, new_entry.node.scope_level, new_entry.node.scope_name)
                if not isDefinition:
                    self.table_entries.append(new_entry)
        else:
            def_entry = []
            for entry in definitionScope.entries:
                if entry.kind == "parameter":
                    def_entry.append(entry)

            if definitionSymbol.type != symbol.type:
                raise ValueError(f"function redefinition return type mismatches\nfunction definition = {definitionSymbol.type}\nfunction redefinition = {symbol.type}")

            if len(def_entry) != len(self.parameters):
                raise ValueError(f"function redefinition parameter list type mismatches\nfunction definition len = {len(def_entry)}\nfunction redefinition len = {len(self.parameters)}")

            table_entry_iterator = iter(self.table_entries)

            for table_entry in table_entry_iterator:
                if table_entry.name == symbol.name:
                    for entry, old_entry in zip(self.parameters, def_entry):
                        param_entry = next(table_entry_iterator)
                        if entry.type != old_entry.type:
                            raise TypeError(f"function redefinition parameter type mismatches => {entry.type} | {old_entry.type}")
                        else:
                            if entry.name != old_entry.name:
                                old_entry.name = entry.name
                                param_entry.name = old_entry.name

                    break

        self.parameters = []

        # Correctly update parent's entries by filtering out forwarded entries
        # self.current_scope.entries = [entry for entry in child_scope.parent.entries if entry not in forward_entries]

        if not isDefinition:
            self.current_scope.children.append(child_scope)
            self.current_scope.entries.append(symbol)

        self.function_definition = True
        if not isDefinition:
            self.function_scope = child_scope
            self.function_symbol = symbol
        else:
            self.function_scope = definitionScope
            self.function_symbol = definitionSymbol

    def add_symbol(self, symbol):
        """
            add the symbol object to the current scope
        """

        if not isinstance(symbol, SymbolEntry):
            raise ValueError("Incorrect type of object")
        
        if isinstance(symbol.name,str) and symbol.name[-1] == '$':
            c = 0
            while symbol.name[-1] == '$':
                c+=1
                symbol.name = symbol.name[:-1]
            symbol.type = c*'*' + symbol.type
        
        if symbol.kind != "function":
            if "void" in (symbol.type).split(" "):
                raise ValueError("void type is not allowed for variables")

        for entry in self.current_scope.entries:
            if strict_equal(entry.name, symbol.name):
                if entry.kind != "constant":
                    raise ValueError(f"Duplicate symbol '{symbol.name}' in scope {self.current_scope_name}")
                else:
                    return
                
        if self.function_definition:
            self.function_definition = False
            self.function_scope = None
            self.function_symbol = None
        
        if self.to_add_child:
            self.to_add_child = False
            symbol.child = self.the_child
            self.the_child = None 

        symbol.node = self.current_scope

        if not symbol.isForwardable:
            self.current_scope.entries.append(symbol)
        else:
            for entry in self.parameters:
                if strict_equal(entry.name, symbol.name):
                    if entry.kind != "constant":
                        raise ValueError(f"Duplicate symbol '{symbol.name}' in scope {self.current_scope_name}")
                    else:
                        return
            self.parameters.append(symbol)

        if not symbol.isForwardable:
            c = 0
            if not isinstance(symbol.name,str) or symbol.name[-1] != '$':
                
                entry = SymbolTableEntry(symbol.name, symbol.type, symbol.kind, symbol, symbol.node, self.current_scope_level, self.current_scope_name)
                self.table_entries.append(entry)
            else:
                while symbol.name[-1] == '$':
                    symbol.name = symbol.name[:-1]
                    c += 1
                
                entry = SymbolTableEntry(symbol.name, c* '*' + symbol.type, symbol.kind, symbol, symbol.node, self.current_scope_level, self.current_scope_name,symbol.refsto)
                self.table_entries.append(entry)
        
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
    
    def search_struct(self, struct_object, identifier):
        field_chain = struct_object.split('.')

        if symtab.lookup(field_chain[0]) is None:
            raise Exception(f"{field_chain[0]} not declared")
        
        field_chain[0] = symtab.lookup(field_chain[0]).type.split(' ')[-1]
        current_scope = self.root

        for scope in field_chain:
            found = False
            for entry in current_scope.entries:
                if entry.name == scope:
                    current_scope = entry.child
                    found = True
                    break

            if not found:
                return None
            
        for entry in current_scope.entries:
            if entry.name == identifier:
                return entry.type

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
