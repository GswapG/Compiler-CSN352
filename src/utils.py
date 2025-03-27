def spaced(word):
    new_word = ""
    for i in range(len(word)):
        if len(new_word) == 0:
            if word[i] != ' ':
                new_word += word[i]
        else:
            if word[i] == ' ':
                if new_word[-1] != ' ':
                    new_word += word[i]
            else:
                new_word += word[i]
    return new_word

def trim_value(type, value):
    """
    trim out value qualifiers from a type in the middle
    """
    if isinstance(type, str):
        # if type starts with value, just strip the beginning
        if type.startswith(f"{value} "):
            type_without_value = type[len(f"{value} "):]
            return spaced(type_without_value)
        
        # if variable type is value char** c
        # then symbol table entry type is "**value char"
        # in that case, i'll strip all the beginning ** and then strip value if it exists
        # and then return **char (for example)
        elif f"{value} " in type:
            type_without_value = type.replace(f"{value} ", "", 1)
            return spaced(type_without_value)

    return type

def strip_value(type, value):
    """
    strip out value qualifiers from a type from the beginning
    """

    if isinstance(type, str):
        # if type starts with value, just strip the beginning
        if type.startswith(f"{value} "):
            type_without_value = type[len(f"{value} "):]
            return type_without_value
        
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

def validate_relational_operands(left_vars, right_vars, symtab, allow_int_float):
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
            if check_types(left_type, right_type, allow_int_float):
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


def check_vars_type(vars_list, expected_type, op_name, symtab, allow_int_float=False):

    for var in vars_list:
        d, r, clean_var = count_deref_ref(var)
        type_ = get_type_from_var(clean_var, d, r, symtab)
        # Compare types after stripping any trailing spaces.
        # Additionally, if the variable represents a struct field or is not a function,
        # then ensure the types are compatible.
        if check_types(type_, expected_type, allow_int_float) and (
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
        base_type = trim_value(entry.type, "const")
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

def validate_assignment(lhs_entry, lhs_effective_type, operator, rhs_vars, symtab, allow_int_float=False, no_float=False):

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
        if check_types(rhs_effective, lhs_effective_type, allow_int_float):
            raise ValueError(f"Type mismatch in assignment of {lhs_entry.name} and {rhs_entry.name}\n {lhs_effective_type} vs {rhs_effective}")

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
            if (trim_value(func_params[params_ptr].type, "const") != 
                trim_value(argument_list[argument_ptr], "const")):
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
        
def dominating_type(type1, type2):
    types1 = type1.split(' ')
    types2 = type2.split(' ')

    allowed_int = ['signed', 'unsigned', 'short', 'long', 'int', 'char']
    # allowed_double = ['signed', 'unsigned', 'float', 'double']
    
    label1 = None
    label2 = None

    if "double" in types1 and "double" in types2:
        return True
    else:
        if "double" not in types1 and "double" not in types2:
            if "float" in types1 and "float" in types2:
                return True
            else:
                if "float" not in types1 and "float" not in types2:
                    if "float" in types1 and "float" in types2:
                        return True

                else:
                    if "float" in types1:
                        return True
                    else:
                        return False

        else:
            if "double" in types1:
                return True
            else:
                return False

def get_label(type):
    type = trim_value(type, "const")
    type = trim_value(type, "unsigned")
    type = trim_value(type, "signed")
    
    types = type.split(' ')

    allowed_int = ['signed', 'unsigned', 'short', 'long', 'int', 'char']

    label = None
    if ("float" in types) or ("double" in types):
        label = "float"
    elif all(t in allowed_int for t in types):
        label = "int"

    return label

        
def check_types(type1, type2, allow_int_float=False):
    ## implicit type conversion
    if type1 == type2:
        return False
    
    ptr1 = True if type1.startswith("*") else False
    ptr2 = True if type2.startswith("*") else False 

    if (ptr1 and not ptr2) or (ptr2 and not ptr1):
        return True 
    
    elif ptr1 and ptr2:
        deref_count1 = 0
        clean_ptr1 = type1

        deref_count2 = 0
        clean_ptr2 = type2

        while isinstance(clean_ptr1, str) and clean_ptr1.startswith("*"):
            deref_count1 += 1
            clean_ptr1 = clean_ptr1[1:]

        while isinstance(clean_ptr2, str) and clean_ptr2.startswith("*"):
            deref_count2 += 1
            clean_ptr2 = clean_ptr2[1:]

        if deref_count1 != deref_count2:
            return True 

        if deref_count1 == deref_count2 and deref_count1 >= 2:
            if clean_ptr1 != clean_ptr2:
                return True
            else:
                return False
        
        clean_ptr1 = trim_value(clean_ptr1, "const")
        clean_ptr1 = trim_value(clean_ptr1, "unsigned")
        clean_ptr1 = trim_value(clean_ptr1, "signed")
        clean_ptr1 = trim_value(clean_ptr1, "static")
        
        clean_ptr2 = trim_value(clean_ptr2, "const")
        clean_ptr2 = trim_value(clean_ptr2, "unsigned")
        clean_ptr2 = trim_value(clean_ptr2, "signed")
        clean_ptr2 = trim_value(clean_ptr2, "static")

        if clean_ptr1 != clean_ptr2:
            return True 
        else:
            return False
        
    type1 = trim_value(type1, "const")
    type1 = trim_value(type1, "unsigned")
    type1 = trim_value(type1, "signed")
    
    type2 = trim_value(type2, "const")
    type2 = trim_value(type2, "unsigned")
    type2 = trim_value(type2, "signed")

    types1 = type1.split(' ')
    types2 = type2.split(' ')
    
    allowed_int = ['signed', 'unsigned', 'short', 'long', 'int', 'char']

    label1 = None
    label2 = None

    if ("float" in types1) or ("double" in types1):
        label1 = "float"
    elif all(t in allowed_int for t in types1):
        label1 = "int"

    if ("float" in types2) or ("double" in types2):
        label2 = "float"
    elif all(t in allowed_int for t in types2):
        label2 = "int"

    if allow_int_float:
        if label1 is not None and label2 is not None:
            return False
        else:
            return True
    else:
        if label1 is not None and label2 is not None:
            if label1 != label2:
                return True
            else:
                return False 
        return True

    return True