from .helpers import *
from .compatible import *
from .symtab_helpers import *
from .exceptions import *
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
        braces_count = 0
        if var[-1] == ']':
            braces_count = var.count("]")
            var = var[:-2 * braces_count]

        if symtab.lookup(var) is not None:
            kind = symtab.lookup(var).kind
            if "D-array" in kind:
                if str(kind[0]) != str(braces_count):
                    raise CompileException("Invalid array access")

        d, r, clean_var = count_deref_ref(var)
        if symtab.lookup(clean_var) is None:
            raise CompileValueError(f"No symbol '{clean_var}' in the symbol table")
    
    # Compare types between left and right operands.
    for var in left_vars:
        d, r, clean_var = count_deref_ref(var)
        left_type = get_type_from_var(clean_var, d, r, symtab)
        for var2 in right_vars:
            d2, r2, clean_var2 = count_deref_ref(var2)
            right_type = get_type_from_var(clean_var2, d2, r2, symtab)
            if argument_type_compatibility(left_type, right_type):
                raise CompileValueError(f"Incompatible relational op with '{clean_var}' and '{clean_var2}'")

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
                    raise CompileException("Invalid array access")
            else:
                decay = True

    if isinstance(var, str) and '.' in var:
        # struct member: "structName identifier"
        if symtab.lookup(var) is not None:
            var_ = symtab.lookup(var)
            type_ = var_.type

            if kind_check is not None and not any(fnmatch.fnmatch(var_.kind, pattern) for pattern in kind_check):
                raise CompileTypeError("Value can only be assigned to variable/param types!")
        
        else:
            struct_scope, identifier = var.rsplit(".", 1)
            entry_type = symtab.search_struct(struct_scope, identifier)[0]
            if entry_type is None:
                raise CompileException(f"identifier |{identifier}| does not exist in the struct |{struct_scope}|")
            
            type_ = entry_type
    else:
        if symtab.lookup(var) is None:
            raise CompileException(f"{var} does not exist in the scope")
        print(var)
        var_ = symtab.lookup(var)
        type_ = var_.type

        if kind_check is not None and not any(fnmatch.fnmatch(var_.kind, pattern) for pattern in kind_check):
            raise CompileTypeError("Value can only be assigned to variable/param types!")

    # Process dereference operations: remove leading '*' for each '@'
    for _ in range(deref_count):
        if isinstance(type_, str) and (type_.startswith('*')):
            type_ = type_[1:]
        else:
            if decay:
                continue
            raise CompileTypeError("Invalid Deref Op")

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
            raise CompileValueError(f"Incompatible {op_name} op with '{clean_var}'")

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
        entry = symtab.search_struct(struct_name, field_name)[0]
        if entry is None:
            raise CompileValueError(f"identifier {field_name} does not exist in the struct {struct_name}")
        return entry
    else:
        entry = symtab.lookup(data)
        if entry is None:
            raise CompileValueError(f"No symbol '{data}' in the symbol table")
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
            raise CompileTypeError("Invalid deref operation")
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
                raise CompileException(f"identifier {clean_rhs} does not exist in the scope")
            
            else:
                kind = symtab.lookup(clean_rhs).kind
                if "D-array" in kind:
                    if str(brace_count) != str(kind[0]):
                        raise CompileException(f"Invalid array access")
        else:
            if symtab.lookup(clean_rhs) is None:
                raise CompileException(f"identifier {clean_rhs} does not exist in the scope")
            else:
                if "D-array" in symtab.lookup(clean_rhs).kind:
                    rhs_effective = "*" + rhs_effective

        # Compare after stripping trailing spaces.
        if implicit_type_compatibility(rhs_effective, lhs_effective_type, allow_int_float):
            raise CompileValueError(f"Type mismatch in assignment\n {lhs_effective_type} vs {rhs_effective}")

        if no_float:
            if get_label(rhs_effective) == "float" or get_label(lhs_effective_type) == "float":
                raise CompileValueError(f"Cannot use {operator} operator with floating type")

def argument_param_match(argument_list, func_params):
    argument_ptr = 0
    params_ptr = 0

    while argument_ptr < len(argument_list) and params_ptr < len(func_params):
        if func_params[params_ptr].type == '...':
            argument_ptr += 1
            pass
        else:
            print(argument_list[argument_ptr],func_params[params_ptr].type)
            if argument_type_compatibility(func_params[params_ptr].type, argument_list[argument_ptr]):
                raise CompileException(f"Invalid Function Parameters => {trim_value(func_params[params_ptr].type, 'const')} | {trim_value(argument_list[argument_ptr], 'const')}")
            else:
                argument_ptr += 1 
                params_ptr += 1

    if argument_ptr != len(argument_list):
        raise CompileException("Invalid Function Parameter Length")
    
    if params_ptr != len(func_params):
        if params_ptr == len(func_params) - 1 and func_params[params_ptr].type =='...':
            pass

        else:
            raise CompileException("Invalid Function Parameter Length")
        
def argument_type_compatibility(type1, type2):
    """
        type1 -> func param
        type2 -> argument param
    """
    ## implicit type conversion
    if type1 is None:
        raise CompileException("lvalue is None")
    
    if type2 is None:
        raise CompileException("rvalue is None")

    if type1 == type2:
        return False
    
    ptr1 = True if type1.startswith("*") else False
    ptr2 = True if type2.startswith("*") else False

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

    if not ptr1 and not ptr2:
        type1 = trim_value(type1, "const")
        type1 = trim_value(type1, "unsigned")
        type1 = trim_value(type1, "signed")
        type1 = trim_value(type1, "static")
        
        if "enum" in type1:
            type1 = "int"

        type2 = trim_value(type2, "const")
        type2 = trim_value(type2, "unsigned")
        type2 = trim_value(type2, "signed")
        type2 = trim_value(type2, "static")

        if "enum" in type2:
            type2 = "int"

        types1 = type1.split(' ')
        types2 = type2.split(' ')
        
        allowed_int = ['signed', 'unsigned', 'short', 'long', 'int', 'char']

        label1 = None
        label2 = None

        if ("float" in types1) or ("double" in types1):
            label1 = "float"
        elif any(t in allowed_int for t in types1):
            label1 = "int"

        if ("float" in types2) or ("double" in types2):
            label2 = "float"
        elif any(t in allowed_int for t in types2):
            label2 = "int"

        if label1 is not None and label2 is not None:
            return False
        else:
            return True

    elif ptr1 and not ptr2:
        allowed_int = ['signed', 'unsigned', 'short', 'long', 'int', 'char']
        
        type2 = trim_value(type2, "const")
        type2 = trim_value(type2, "unsigned")
        type2 = trim_value(type2, "signed")
        type2 = trim_value(type2, "static")

        if "enum" in type2:
            type2 = "int"

        types2 = type2.split(' ')

        label1 = None
        label2 = None

        if ("float" in types2) or ("double" in types2):
            label2 = "float"
        elif any(t in allowed_int for t in types2):
            label2 = "int"

        if label2 != "int":
            return True
        else:
            return False

    elif ptr2 and not ptr1:
        allowed_int = ['signed', 'unsigned', 'short', 'long', 'int', 'char']
        
        type1 = trim_value(type1, "const")
        type1 = trim_value(type1, "unsigned")
        type1 = trim_value(type1, "signed")
        type1 = trim_value(type1, "static")

        if "enum" in type1:
            type1 = "int"

        types1 = type1.split(' ')

        label1 = None
        label2 = None

        if ("float" in types1) or ("double" in types1):
            label1 = "float"
        elif any(t in allowed_int for t in types1):
            label1 = "int"

        if label1 != "int":
            return True
        else:
            return False
    
    elif ptr1 and ptr2:
        

        return False
        
    return True

def ternary_type_compatibility(type1, type2, type3):
    if get_label(type1.replace("*", "")) is None:
        raise CompileException("First type in ternary operators should be a scalar type")

    return argument_type_compatibility(type2, type3)

def same_class_compatibility(type1, type2):
    if "*" in type1 or "*" in type2:
        return True
    
    types1 = type1.split(' ')
    types2 = type2.split(' ')

    label1 = None
    label2 = None

    allowed_int = ['signed', 'unsigned', 'short', 'long', 'int', 'char']
    if any(t in allowed_int for t in types1):
        label1 = "int"

    if any(t in allowed_int for t in types2):
        label2 = "int"

    if label1 == label2 and label1 == "int":
        return False
    
    return True

def get_size_from_type(c_type):
    modifiers = ["const", "static", "volatile", "register", "extern", "auto", "restrict"]
    clean_type = c_type.lower()
    
    for modifier in modifiers:
        clean_type = clean_type.replace(modifier, "").strip()
    if '*' in clean_type:
        return 8
    if "char" in clean_type:
        return 1
    elif "short" in clean_type or "int16_t" in clean_type:
        return 2
    elif "int" in clean_type or "int32_t" in clean_type:
        return 4
    elif "long long" in clean_type or "int64_t" in clean_type:
        return 8
    elif "long" in clean_type:
        return 8  
    elif "float" in clean_type:
        return 4
    elif "double" in clean_type:
        if "long" in clean_type:
            return 16 
        return 8
    elif "bool" in clean_type or "_Bool" in clean_type:
        return 1
    elif "void" == clean_type:
        return 0
    
    raise CompileValueError(f"Unknown type for size calculation: {c_type}")
def get_scope_number(scope_name):
    if scope_name == "global":
        return '#0'
    if '@' in scope_name:
        try:
            return '#' + scope_name.split('@')[-1] 
        except ValueError:
            pass
    raise CompileException(f"Invalid scope name format: {scope_name}")