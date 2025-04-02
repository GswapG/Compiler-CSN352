from .helpers import *
from .compatible import *
from .symtab_helpers import *

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

def validate_relational_operands(left_vars, right_vars, symtab, allow_int_float):
    # Validate left variables exist in the symbol table.
    for var in left_vars:
        braces_count = 0
        if var[-1] == ']':
            braces_count = var.count("]")
            var = var[:-2 * braces_count]

        if symtab.lookup(var) is not None:
            kind = symtab.lookup(var).kind
            if "D-array" in kind:
                if str(kind[0]) != str(braces_count):
                    raise Exception("Invalid array access")

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
            if implicit_type_compatibility(left_type, right_type, allow_int_float):
                raise ValueError(f"Incompatible relational op with '{clean_var}' and '{clean_var2}'")

def get_type_from_var(var, deref_count, ref_count, symtab, kind_check=None):
    braces_count = 0
    decay = False
    if var[-1] == ']':
        braces_count = var.count("]")
        var = var[:-2 * braces_count]

    if symtab.lookup(var) is not None:
        kind = symtab.lookup(var).kind
        if "D-array" in kind:
            if braces_count > 0:
                if str(kind[0]) != str(braces_count):
                    raise Exception("Invalid array access")
            else:
                decay = True

    if isinstance(var, str) and '.' in var:
        # struct member: "structName identifier"
        if symtab.lookup(var) is not None:
            var_ = symtab.lookup(var)
            type_ = var_.type

            if kind_check is not None and not any(fnmatch.fnmatch(var_.kind, pattern) for pattern in kind_check):
                raise TypeError("Value can only be assigned to variable/param types!")
        
        else:
            struct_scope, identifier = var.rsplit(".", 1)
            entry_type = symtab.search_struct(struct_scope, identifier)
            if entry_type is None:
                raise Exception(f"identifier |{identifier}| does not exist in the struct |{struct_scope}|")
            
            type_ = entry_type
    else:
        if symtab.lookup(var) is None:
            raise Exception(f"{var} does not exist in the scope")
        
        var_ = symtab.lookup(var)
        type_ = var_.type

        if kind_check is not None and not any(fnmatch.fnmatch(var_.kind, pattern) for pattern in kind_check):
            raise TypeError("Value can only be assigned to variable/param types!")

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
    
    if decay:
        type_ = "*" + type_

    return type_

def implicit_type_check_list(vars_list, expected_type, op_name, symtab, allow_int_float=False):

    for var in vars_list:
        d, r, clean_var = count_deref_ref(var)
        type_ = get_type_from_var(clean_var, d, r, symtab)
        # Compare types after stripping any trailing spaces.
        # Additionally, if the variable represents a struct field or is not a function,
        # then ensure the types are compatible.

        if implicit_type_compatibility(type_, expected_type, allow_int_float) and (
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

def effective_type(entry_type, deref_count, ref_count, remove_const=False):
    # Remove "const " from the type for assignment checking, if present.
    if remove_const:
        base_type = trim_value(entry_type, "const")
    else:
        base_type = entry_type

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

def validate_assignment(lhs_effective_type, operator, rhs_vars, symtab, allow_int_float=False, no_float=False):

    for rhs_var in rhs_vars:
        # For struct members in RHS, handle separately.
        d, r, clean_rhs = count_deref_ref(rhs_var)
        rhs_effective = get_type_from_var(clean_rhs, d, r, symtab)

        if clean_rhs[-1] == ']':
            brace_count = clean_rhs.count("]")
            clean_rhs = clean_rhs[:-2 * brace_count]

            if symtab.lookup(clean_rhs) is None:
                raise Exception(f"identifier {clean_rhs} does not exist in the scope")
            
            else:
                kind = symtab.lookup(clean_rhs).kind
                if "D-array" in kind:
                    if str(brace_count) != str(kind[0]):
                        raise Exception(f"Invalid array access")
        else:
            if symtab.lookup(clean_rhs) is None:
                raise Exception(f"identifier {clean_rhs} does not exist in the scope")
            else:
                if "D-array" in symtab.lookup(clean_rhs).kind:
                    rhs_effective = "*" + rhs_effective

        # Compare after stripping trailing spaces.
        if implicit_type_compatibility(rhs_effective, lhs_effective_type, allow_int_float):
            raise ValueError(f"Type mismatch in assignment\n {lhs_effective_type} vs {rhs_effective}")

        if no_float:
            if get_label(rhs_effective) == "float" or get_label(lhs_effective_type) == "float":
                raise ValueError(f"Cannot use {operator} operator with floating type")

def argument_param_match(argument_list, func_params):
    argument_ptr = 0
    params_ptr = 0

    while argument_ptr < len(argument_list) and params_ptr < len(func_params):
        if func_params[params_ptr].type == '...':
            argument_ptr += 1
            pass
        else:
            if implicit_type_compatibility(func_params[params_ptr].type, argument_list[argument_ptr], True):
                raise Exception(f"Invalid Function Parameters => {trim_value(func_params[params_ptr].type, 'const')} | {trim_value(argument_list[argument_ptr], 'const')}")
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
        
