from collections import defaultdict
from collections import deque
marker = defaultdict(list)
class SymbolEntry:
    def __init__(self, name, type, kind, scope_level, scope_name, size, offset, line):
        self.name = name
        self.type = type
        self.kind = kind          # 'variable', 'function', 'parameter'
        self.scope_level = scope_level
        self.scope_name = scope_name
        self.size = size           # Size in bytes
        self.offset = offset       # Stack offset (for local variables)
        self.line = line           # Source line number

class SymbolTable:
    def __init__(self):
        self.scopes = deque()       # Stack of scopes (deque for efficient stacking)
        self.current_scope_level = -1
        self.current_scope_name = "global"
        self.offset_counter = {}    # Track offsets per scope level
        self.enter_scope()          # Initialize global scope
    
    def clear(self):
        """Reset the symbol table to its initial state"""
        self.scopes.clear()  # Remove all scopes
        self.current_scope_level = -1
        self.current_scope_name = "global"
        self.offset_counter = {}
        self.enter_scope()  # Recreate global scope
    
    def enter_scope(self, scope_name=None):
        """Create a new scope"""
        self.scopes.append({})
        self.current_scope_level += 1
        print("plus")
        self.current_scope_name = scope_name or f"block@{self.current_scope_level}"
        if self.current_scope_level==0:
            self.current_scope_name = "global"
        self.offset_counter[self.current_scope_level] = 0

    def exit_scope(self):
        """Leave current scope"""
        for j in marker[self.current_scope_level]:
            for i in list(self.scopes[j[1]]):
                if i == j[0].name:
                    self.scopes[j[1]].pop(i)
        print("minus")
        marker[self.current_scope_level].clear()
        if self.current_scope_level > 0:
            self.scopes.pop()
            self.current_scope_level -= 1
            self.current_scope_name = "global" if self.current_scope_level == 0 else f"block@{self.current_scope_level}"

    def add_symbol(self, symbol):
        """Add symbol to current scope"""
        current_scope = self.scopes[-1]
        if symbol.name in current_scope:
            raise ValueError(f"Duplicate symbol '{symbol.name}' in scope {self.current_scope_name}")
        
        # Calculate offset for variables/parameters
        if symbol.kind in ['variable', 'parameter']:
            symbol.offset = self.offset_counter[self.current_scope_level]
            self.offset_counter[self.current_scope_level] += symbol.size
        
        current_scope[symbol.name] = symbol
        print("added symbol",symbol.name)
        print(symtab)

    def lookup(self, name):
        """Search for symbol in all enclosing scopes"""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def __str__(self):
        """Pretty-print symbol table"""
        headers = ["Name", "Type", "Kind", "Scope", "ScopeName", "Size", "Offset", "Line"]
        rows = []
        
        for scope in self.scopes:
            for sym in scope.values():
                rows.append([
                    sym.name, sym.type, sym.kind, sym.scope_level,
                    sym.scope_name, sym.size, sym.offset, sym.line
                ])
        
        return tabulate(rows, headers=headers, tablefmt="grid")

# Type size mapping (simplified)
TYPE_SIZES = {
    'int': 4,
    'float': 4,
    'char': 1,
    'void': 0
}

def get_type_size(type_specifiers):
    """Calculate size based on type specifiers"""
    # Simplified implementation
    return TYPE_SIZES.get(type_specifiers[0], 0)

# Install tabulate for pretty-printing
try:
    from tabulate import tabulate
except ImportError:
    print("Install tabulate for better output: pip install tabulate")
    def tabulate(*args, **kwargs):
        return str(args[0])

symtab = SymbolTable()