from .helpers import *

# helper functions for type compatibility checks

def validate_c_datatype(data_type, symtab):
    valid_type_patterns = [
        ['char'],
        ['short'],
        ['short', 'int'],
        ['int'],
        ['long'],
        ['long', 'int'],
        ['long', 'long'],
        ['long', 'long', 'int'],
        ['long', 'double'],
        ['float'],
        ['double'],
        ['void']
    ]

    allowed_with_sign = [
        ['char'],
        ['short'],
        ['short', 'int'],
        ['int'],
        ['long'],
        ['long', 'int'],
        ['long', 'long'],
        ['long', 'long', 'int']
    ]

    allowed_keywords = {'signed', 'unsigned', 'short', 'long', 'int', 'char', 'float', 'double', 'void'}

    
    data_type = data_type.lstrip('*')
    tokens = data_type.strip().split()

    if(tokens[0]=="typedef"):
        tokens = tokens[1:]
    
    if tokens[0]=="const":
        tokens=tokens[1:]
        if tokens[0]=="static":
            tokens=tokens[1:]

    elif tokens[0]=="static":
        tokens=tokens[1:]
        if tokens[0]=="const":
            tokens=tokens[1:]

    if tokens[0] == "struct" or tokens[0] == "union" or tokens[0] == "enum":
        identifier = tokens[0]
        tokens = tokens[1:]
        for c in tokens:
            if c in allowed_keywords:
                raise ValueError(f"Invalid data type structure '{data_type}'.")
            
            elif identifier != "enum":
                if symtab.lookup(c) is None:
                    raise Exception(f"Identifier {c} does not exist in the current scope")

                if symtab.lookup(c).kind != identifier:
                    raise Exception(f"Identifier {c} does not exist in the current scope")
                
        return True

    abcd = symtab.lookup(tokens[0])
    if abcd is not None and abcd.type == "struct":
        return True
    
    # Check for invalid tokens
    for token in tokens:
        if token not in allowed_keywords:
            raise ValueError(f"Invalid token '{token}' in data type '{data_type}'.")
    
    has_sign = False
    sign = None
    if tokens and tokens[0] in ('signed', 'unsigned'):
        sign = tokens[0]
        has_sign = True
        type_tokens = tokens[1:]
        # Handle case where sign is present but no other tokens (e.g., 'unsigned')
        if not type_tokens:
            type_tokens = ['int']
    else:
        type_tokens = tokens
    
    # Check if the type structure is valid
    valid_type = False
    for pattern in valid_type_patterns:
        if type_tokens == pattern:
            valid_type = True
            break
    if not valid_type:
        raise ValueError(f"Invalid data type structure '{data_type}'.")
    
    # Check if sign is allowed for the given type
    if has_sign:
        if type_tokens not in allowed_with_sign:
            raise ValueError(f"Sign specifier '{sign}' not allowed for data type '{data_type}'.")
    
    return True

def dominating_type(type1, type2):
    types1 = type1.split(' ')
    types2 = type2.split(' ')

    if "double" in types1 and "double" in types2:
        return True
    else:
        if "double" not in types1 and "double" not in types2:
            if "float" in types1 and "float" in types2:
                return True
            else:
                if "float" not in types1 and "float" not in types2:
                    if "int" in types1 and "int" in types2:
                        return True
                    else:
                        if "int" not in types1 and "int" not in types2:
                            if "short" in types1 and "short" in types2:
                                return True
                            else:
                                if "short" not in types1 and "short" not in types2:
                                    if "char" in types1 and "char" in types2:
                                        return True
                                    else:
                                        if type1 == type2:
                                            return True
                                        else:
                                            raise Exception(f"Unexpected types received {types1} {types2}")
                                else:
                                    if "short" in types1:
                                        return True
                                    else:
                                        return False
                        else:
                            if "int" in types1:
                                return True
                            else:
                                return False
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
    type = trim_value(type, "static")
    
    types = type.split(' ')

    allowed_int = ['signed', 'unsigned', 'short', 'long', 'int', 'char']

    label = None
    if ("float" in types) or ("double" in types):
        label = "float"
    elif all(t in allowed_int for t in types):
        label = "int"

    return label

def get_unqualified_type(type):
    if type is None:
        raise Exception("Invalid type provided")
    
    # add type qualifiers to trim here
    type = trim_value(type, "const")
    return type

def strict_unqualified_compatibility(type1, type2):
    if type1 is None:
        raise Exception("Invalid type provided")
    
    if type2 is None:
        raise Exception("Invalid type provided")
    
    type1 = get_unqualified_type(type1)
    type2 = get_unqualified_type(type2)

    if type1 != type2:
        return True 
    
    return False

def strict_compatibility(type1, type2):
    if type1 is None:
        raise Exception("Invalid type provided")
    
    if type2 is None:
        raise Exception("Invalid type provided")

    if type1 != type2:
        return True 
    
    return False

def array_type_decay(type):
    if type is None:
        return type
    
    if type.count("[") > 1:
        raise Exception(f"Invalid type {type}")
    
    if type.count("[") == 1:
        type = type.replace("[", "")
        type = type.replace("]", "")
        type = type.strip(' ')
        type = "*" + type

    return type

def array_base_type(type):
    if type is None:
        raise Exception("Invalid Type received")

    type = type.replace("[", "")
    type = type.replace("]", "")
    type = type.strip(' ')
    return type

def implicit_type_compatibility(type1, type2, allow_int_float=False):
    ## implicit type conversion
    if type1 is None:
        raise Exception("lvalue is None")
    
    if type2 is None:
        raise Exception("rvalue is None")

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

        
        if clean_ptr1 == "void" or clean_ptr2 == "void":
            return False

        elif clean_ptr1 != clean_ptr2:
            return True 

        else:
            return False
        
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

def addition_compatibility(type1, type2):
    # print(type1, type2)
    if type1 is None:
        raise Exception("lvalue is None")
    
    if type2 is None:
        raise Exception("rvalue is None")
    
    save_type1 = type1
    save_type2 = type2
    
    type1 = trim_value(type1, "const")
    type1 = trim_value(type1, "unsigned")
    type1 = trim_value(type1, "signed")
    type1 = trim_value(type1, "static")

    type2 = trim_value(type2, "const")
    type2 = trim_value(type2, "unsigned")
    type2 = trim_value(type2, "signed")
    type2 = trim_value(type2, "static")

    if "*" in type1 and not implicit_type_compatibility(type2, "int"):
        # pointers can always be added to an integer type
        return type1

    if "*" in type1:
        type1 = type1.lstrip("*")

        if type1 == type2:
            # print(save_type1)
            return save_type1
        
        else:
            raise TypeError(f"Incompatible types {save_type1} {save_type2} for the operation addition")

    if "*" in type2:
        type2 = type2.lstrip("*")

        if type2 == type1:
            return save_type2
        
        else:
            raise TypeError(f"Incompatible types {save_type1} {save_type2} for the operation addition")

    raise Exception(f"This method should only be called when either one of the types is a pointer to an object, but the types passed were: {save_type1} and {save_type2}")

def subtraction_compatibility(type1, type2):
    if type1 is None:
        raise Exception("lvalue is None")
    
    if type2 is None:
        raise Exception("rvalue is None")
    
    save_type1 = type1
    save_type2 = type2

    if "*" in type1 and "*" in type2:
        # only strip the qualifiers for singled pointer and then check for compatibility and return the stripped pointers
        # for double pointers, it should exactly match without the *

        if type1.count("*") != type2.count("*"):
            raise Exception(f"Incompatible types for subtraction operator: {save_type1} and {save_type2}")

        if type1.count("*") == 1 and type2.count("*") == 1:
            type1 = trim_value(type1, "const")
            type1 = trim_value(type1, "static")

            type2 = trim_value(type2, "const")
            type2 = trim_value(type2, "static")

        if type1 == type2:
            return type1.lstrip("*")
        
        else:
            raise Exception(f"Incompatible types for subtraction operator: {save_type1} and {save_type2}")
 
    elif "*" in type2:
        raise Exception(f"Subtraction operator is not compatible with the first operand type: '{save_type1}' being an integer type and the second operand type: '{save_type2}' being a pointer type")

    elif "*" in type1: 
        type1 = trim_value(type1, "const")
        type1 = trim_value(type1, "unsigned")
        type1 = trim_value(type1, "signed")
        type1 = trim_value(type1, "static")

        type2 = trim_value(type2, "const")
        type2 = trim_value(type2, "unsigned")
        type2 = trim_value(type2, "signed")
        type2 = trim_value(type2, "static")

        type1 = type1.lstrip("*")

        if type1 == type2:
            return save_type1
        
        else:
            raise TypeError(f"Incompatible types {save_type1} {save_type2} for the operation addition")

    raise Exception(f"This method should only be called when either one of the types is a pointer to an object, but the types passed were: {save_type1} and {save_type2}")    

def compatible_cast(cast_type, expression_type):
    if cast_type is None:
        raise Exception(f"cast type is invalid")
    
    if expression_type is None:
        raise Exception(f"expression type is invalid")
    
    if "*void" == cast_type or "*void" == expression_type:
        return True
    
    if "struct" in cast_type and "struct" in expression_type:
        if cast_type != expression_type:
            return False 
        
        else:
            return True
        
    if "union" in cast_type and "union" in expression_type:
        if cast_type != expression_type:
            return False 
        
        else:
            return True
    
    if "struct" in cast_type and "union" not in expression_type:
        return False
    
    if "union" in cast_type and "struct" not in expression_type:
        return False

    if "*" in cast_type and get_label(expression_type) == "float":
        return False
    
    if "*" in expression_type and get_label(cast_type) == "float":
        return False

    # handle other casting between other types apart from struct or union here if required
    return True   

def ternary_type_compatibility(type1, type2, type3):
    if get_label(type1.replace("*", "")) is None:
        raise Exception("First type in ternary operators should be a scalar type")

    return implicit_type_compatibility(type2, type3, True)

