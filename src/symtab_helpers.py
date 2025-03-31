# helper functions for symbol table entries

def compute_struct(symbol, symtab):
    entries = symbol.child.entries
    maximum_alignment = 0
    for entry in entries:
        maximum_alignment = max(maximum_alignment, entry.size)

    if maximum_alignment == 0:
        return maximum_alignment

    struct_entries = []
    table_entries = symtab.table_entries
    scope_level = symbol.node.scope_level

    count = 0
    for entry in reversed(table_entries):
        if scope_level + 1 == entry.scope:
            count += 1
            struct_entries.append(entry)

        if count == len(entries):
            break   

    struct_entries.reverse()
    table_ptr = 0

    size = 0
    for entry in entries:
        if entry.kind != "constant":
            offset = size % entry.size
            if offset == 0:
                offset = entry.size

            size += (entry.size - offset)
            entry.offset = size
            struct_entries[table_ptr].offset = entry.offset
            
            size += entry.size
        else:
            entry.offset = 0
            struct_entries[table_ptr].offset = entry.offset

        table_ptr += 1

    offset = size % maximum_alignment
    if offset == 0:
        offset = maximum_alignment
    
    size += (maximum_alignment - offset)
    return size

def compute_union(symbol, symtab):
    entries = symbol.child.entries
    maximum_alignment = 0
    for entry in entries:
        maximum_alignment = max(maximum_alignment, entry.size)

    if maximum_alignment == 0:
        return maximum_alignment
    
    union_entries = []
    table_entries = symtab.table_entries
    scope_level = symbol.node.scope_level

    count = 0
    for entry in reversed(table_entries):
        if scope_level + 1 == entry.scope:
            count += 1
            union_entries.append(entry)

        if count == len(entries):
            break   

    union_entries.reverse()
    table_ptr = 0

    size = 0
    for entry in entries:
        entry.offset = size
        union_entries[table_ptr].offset = entry.offset
        table_ptr += 1

    return maximum_alignment

def restructure_enum(symtab):
    table_entries = symtab.table_entries
    for entry in reversed(table_entries):
        if entry.kind == "enumerator":
            entry.offset = 0
            entry.node.size -= 4
        else:
            return

def get_size(symbol, symtab):
    if "*" in symbol.type:
        return 8 
    
    if "enum type" in symbol.kind:
        restructure_enum(symtab)
        return 4

    if "enum" in symbol.type:
        return 4
    
    if symbol.kind == "constant":
        return 0
    
    if "struct" == symbol.type:
        return compute_struct(symbol, symtab)
    
    if "union" == symbol.type:
        return compute_union(symbol, symtab)

    if "struct" in symbol.type:
        struct_name = symbol.type.split(' ')[-1]
        if symtab.lookup(struct_name) is None:
            raise Exception(f"Definition of {symbol.type} not found during lookup in the parent scopes")

        return symtab.lookup(struct_name).size
    
    if "union" in symbol.type:
        union_name = symbol.type.split(' ')[-1]
        if symtab.lookup(union_name) is None:
            raise Exception(f"Definition of {symbol.type} not found during lookup in the parent scopes")

        return symtab.lookup(union_name).size

    if "double" in symbol.type:
        return 8
    
    if "float" in symbol.type:
        return 4

    if "long" in symbol.type:
        # long int is 8 bytes in linux but 4 bytes in windows
        return 8

    if "short" in symbol.type:
        return 2
    
    if "char" in symbol.type:
        return 1
    
    if "int" in symbol.type:
        return 4
   