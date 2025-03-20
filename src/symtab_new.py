from collections import defaultdict, deque

class SymbolEntry:
    def __init__(self, name, type, kind, node=None, isForwardable=False):
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
        self.isForwardable = isForwardable

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

class SymbolTableEntry:
    def __init__(self, name, type, kind, scope, scope_name):
        self.name = name 
        self.type = type 
        self.kind = kind 
        self.scope = scope
        self.scope_name = scope_name

class SymbolTable:
    def __init__(self):
        self.root = SymbolEntryNode(0, "global")
        self.current_scope = self.root 
        self.current_scope_name = self.root.scope_name
        self.current_scope_level = self.root.scope_level
        self.table_entries = []

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

        forward_entries = []
        for entry in scope_node.parent.entries:
            if entry.isForwardable:
                forward_entries.append(entry)
                entry.node = scope_node
                entry.isForwardable = False
                scope_node.entries.append(entry)

                # Add to table_entries if not forwardable anymore
                entry = SymbolTableEntry(entry.name, entry.type, entry.kind, entry.node.scope_level, entry.node.scope_name)
                self.table_entries.append(entry)

        # Correctly update parent's entries by filtering out forwarded entries
        scope_node.parent.entries = [entry for entry in scope_node.parent.entries if entry not in forward_entries]

        self.current_scope.children.append(scope_node)
        self.current_scope = scope_node

    def exit_scope(self):
        """
            to exit the scope, dont pop the mess just traverse to the parent back 
        """

        parent = self.current_scope.parent 

        self.current_scope_name = parent.scope_name
        self.current_scope_level = parent.scope_level 
        self.current_scope = parent 

    def add_symbol(self, symbol):
        """
            add the symbol object to the current scope
        """

        if not isinstance(symbol, SymbolEntry):
            raise ValueError("Incorrect type of object")

        for entry in self.current_scope.entries:
            if entry.name == symbol.name:
                # print(entry.type)
                if entry.kind != "constant":
                    raise ValueError(f"Duplicate symbol '{symbol.name}' in scope {self.current_scope_name}")
                else:
                    return
        
        symbol.node = self.current_scope
        self.current_scope.entries.append(symbol)

        if not symbol.isForwardable:
            entry = SymbolTableEntry(symbol.name, symbol.type, symbol.kind, self.current_scope_level, self.current_scope_name)
            self.table_entries.append(entry)

        print("added symbol",symbol.name)
        
    def lookup(self, name):
        scope_pointer = self.current_scope
        while scope_pointer:
            for entry in scope_pointer.entries:
                if entry.name == name:
                    return entry
            scope_pointer = scope_pointer.parent
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

try:
    from tabulate import tabulate

except ImportError:
    print("Install tabulate for better output: pip install tabulate")
    def tabulate(*args, **kwargs):
        return str(args[0])
         
symtab = SymbolTable()
