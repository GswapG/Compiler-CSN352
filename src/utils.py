def trim_const(type):
    """
    trim out const qualifiers from a type in the middle
    """
    if isinstance(type, str):
        # if type starts with const, just strip the beginning
        if type.startswith("const "):
            type_without_const = type[len("const "):]
            return type_without_const
        
        # if variable type is const char** c
        # then symbol table entry type is "**const char"
        # in that case, i'll strip all the beginning ** and then strip const if it exists
        # and then return **char (for example)
        elif type.startswith("*"):
            type_without_const = type
            deref_count = 0

            while len(type_without_const) > 0 and type_without_const.startswith("*"):
                type_without_const = type_without_const[1:]
                deref_count += 1

            if type_without_const.startswith("const "):
                type_without_const = "*" * deref_count + type_without_const[len("const "):]
                return type_without_const

    return type

def strip_const(type):
    """
    strip out constant qualifiers from a type from the beginning
    """

    if isinstance(type, str):
        # if type starts with const, just strip the beginning
        if type.startswith("const "):
            type_without_const = type[len("const "):]
            return type_without_const
        
    return type

def count_deref_ref(var):
    """
    Count dereference (@) and reference (!) prefixes in a variable.
    Returns a tuple: (deref_count, ref_count, cleaned_var)
    """
    deref_count = 0
    ref_count = 0
    # Loop until no leading '@' or '!'
    while isinstance(var, str) and var:
        if var[0] == '@':
            deref_count += 1
            var = var[1:]
        elif var[0] == '!':
            ref_count += 1
            var = var[1:]
        else:
            break
    return deref_count, ref_count, var

def validate_relational_operands(left_vars, right_vars, symtab):
    # Validate left variables exist in the symbol table.
    for var in left_vars:
        d, r, clean_var = count_deref_ref(var)
        if symtab.lookup(clean_var) is None:
            raise ValueError(f"No symbol '{clean_var}' in the symbol table")
    
    # Compare types between left and right operands.
    for var in left_vars:
        d, r, clean_var = count_deref_ref(var)
        left_type = get_type_from_var(clean_var, d, r, symtab)
        for var2 in right_vars:
            d2, r2, clean_var2 = count_deref_ref(var2)
            right_type = get_type_from_var(clean_var2, d2, r2, symtab)
            if left_type.rstrip(' ') != right_type.rstrip(' '):
                raise ValueError(f"Incompatible relational op with '{clean_var}' and '{clean_var2}'")

def get_type_from_var(var, deref_count, ref_count, symtab):

    if isinstance(var, str) and ' ' in var:
        # struct member: "structName identifier"
        name, _, identifier = var.split(' ')
        entry = symtab.search_struct(name, identifier)
        if entry is None:
            raise Exception(f"identifier {identifier} does not exist in the struct {name}")
        
        type_ = entry.type
    else:
        type_ = symtab.lookup(var).type

    # Process dereference operations: remove leading '*' for each '@'
    for _ in range(deref_count):
        if isinstance(type_, str) and type_.startswith('*'):
            type_ = type_[1:]
        else:
            raise TypeError("Invalid Deref Op")

    # Process reference operations: add a '*' for each '!'
    for _ in range(ref_count):
        if isinstance(type_, str):
            type_ = "*" + type_
    return type_


def check_vars_type(vars_list, expected_type, op_name, symtab):

    for var in vars_list:
        d, r, clean_var = count_deref_ref(var)
        type_ = get_type_from_var(clean_var, d, r, symtab)
        # Compare types after stripping any trailing spaces.
        # Additionally, if the variable represents a struct field or is not a function,
        # then ensure the types are compatible.
        if type_.rstrip(' ') != expected_type.rstrip(' ') and (
            (isinstance(clean_var, str) and ' ' in clean_var) or symtab.lookup(clean_var).kind != "function"
        ):
            raise ValueError(f"Incompatible {op_name} op with '{clean_var}'")

def clean_var(var):
    if isinstance(var, str) and ' ' in var:
        parts = var.split(' ')
        if len(parts) >= 2:
            # Assume format "structName ... fieldName"
            return True, (parts[0], parts[-1])
    return False, var

def lookup_symbol(var, symtab):
    is_struct, data = clean_var(var)
    if is_struct:
        struct_name, field_name = data
        entry = symtab.search_struct(struct_name, field_name)
        if entry is None:
            raise ValueError(f"identifier {field_name} does not exist in the struct {struct_name}")
        return entry
    else:
        entry = symtab.lookup(data)
        if entry is None:
            raise ValueError(f"No symbol '{data}' in the symbol table")
        return entry

def process_deref_ref(var):
    deref_count = 0
    ref_count = 0
    while isinstance(var, str) and var:
        if var[0] == '@':
            deref_count += 1
            var = var[1:]
        elif var[0] == '!':
            ref_count += 1
            var = var[1:]
        else:
            break
    return deref_count, ref_count, var

def effective_type(entry, deref_count, ref_count, remove_const=False):
    # Remove "const " from the type for assignment checking, if present.
    if remove_const:
        base_type = trim_const(entry.type)
    else:
        base_type = entry.type

    # Apply dereference operations: remove one level of pointer per '@'
    for _ in range(deref_count):
        if isinstance(base_type, str) and base_type.startswith('*'):
            base_type = base_type[1:]
        else:
            raise TypeError("Invalid deref operation")
    # Apply reference operations: add a '*' per '!'
    for _ in range(ref_count):
        if isinstance(base_type, str):
            base_type = "*" + base_type
    return base_type

def validate_assignment(lhs_entry, lhs_effective_type, rhs_vars, symtab):

    for rhs_var in rhs_vars:
        # For struct members in RHS, handle separately.
        is_struct, data = clean_var(rhs_var)
        if is_struct:
            # Lookup the struct field
            rhs_entry = lookup_symbol(rhs_var, symtab)
            # For struct members, assume no extra deref/ref needed.
            rhs_effective = rhs_entry.type
        else:
            d, r, clean_rhs = process_deref_ref(rhs_var)
            rhs_entry = lookup_symbol(clean_rhs, symtab)
            rhs_effective = effective_type(rhs_entry, d, r, True)
        # Compare after stripping trailing spaces.
        if rhs_effective != lhs_effective_type:
            raise ValueError(f"Type mismatch in assignment of {lhs_entry.name} and {rhs_entry.name}\n {lhs_effective_type} vs {rhs_effective}")

def argument_param_match(argument_list, func_params):
    argument_ptr = 0
    params_ptr = 0

    while argument_ptr < len(argument_list) and params_ptr < len(func_params):
        if func_params[params_ptr].type == '...':
            argument_ptr += 1
            pass
        else:
            if trim_const(func_params[params_ptr].type) != trim_const(argument_list[argument_ptr]):
                raise Exception("Invalid Function Paramters")
            else:
                argument_ptr += 1 
                params_ptr += 1

    if argument_ptr != len(argument_list):
        raise Exception("Invalid Function Parameter Length")
    
    if params_ptr != len(func_params):
        if params_ptr == len(func_params) - 1 and func_params[params_ptr].type =='...':
            pass

        else:
            raise Exception("Invalid Function Parameter Length")
        
def iscompatible(type1, type2):
    pass