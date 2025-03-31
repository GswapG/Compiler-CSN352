import ply.yacc as yacc
import os
from ply import yacc
from .utils import *
from .lexer import *
from .tree import *
from .symtab_new import *
from .ir import *
from .ir_codegen import *

datatypeslhs=[]
returns = set()
constants = defaultdict(lambda: None)

def table_entry(node):
    compound_dtype = ""
    for t in node.dtypes:
        compound_dtype += t
        compound_dtype += " "
    compound_dtype = compound_dtype.strip()
    for var in node.vars:
        stars = ""
        consts = ""
        while isinstance(var, str) and var[-1] == '?':
            stars += "*"
            var = var[:-1]
        while isinstance(var, str) and var[0] == '#':
            consts += " const"
            var = var[1:]
        symbol_table.append((var, compound_dtype + stars + consts))
    if compound_dtype.split(" ")[0] == "typedef":
        for var in node.vars:
            typedef_names.add(str(var))

def p_start_symbol(p):
    '''start_symbol : translation_unit'''
    p[0] = Node("start_symbol",[p[1]])
    IrGen.print_final_code(p[1].ir)
    
# Translation Unit
def p_translation_unit(p):
    '''translation_unit : external_declaration
                       | translation_unit external_declaration'''
    if len(p) == 2:
        p[0] = Node("translation_unit", [p[1]])
    else:
        p[0] = Node("translation_unit", [p[1], p[2]])
        IrGen.translation_unit(p[0].ir,p[1].ir,p[2].ir)

def p_external_declaration(p):
    '''external_declaration : function_definition
                           | declaration'''
    p[0] = Node("external_declaration", [p[1]])

# Expressions
def p_primary_expression(p):
    '''primary_expression : constant
                          | string
                          | LPAREN expression RPAREN
                          | generic_selection'''
    if len(p) == 2:
        p[0] = Node("primary_expression", [p[1]])
        
    elif len(p) == 4:
        p[0] = Node("primary_expression", [p[2]])
        p[0].return_type = p[2].return_type

        p[0].lvalue = p[2].lvalue
        p[0].rvalue = p[2].rvalue

def p_primary_expression_identifier(p):
    '''primary_expression : IDENTIFIER'''

    p[0] = Node("primary_expression_identifier", [p[1]])
    p[0].vars.append(str(p[1]))

    p[0].lvalue = True
    p[0].rvalue = False
    
    c1 = 0
    cpy = p[1]
    
    while isinstance(cpy, str) and cpy[0] == '@':
        c1 += 1
        cpy = cpy[1:]

    check = symtab.lookup(cpy)
    if check is not None:
        p[0].dtypes = check.type
        p[0].return_type = check.type

    IrGen.identifier(p[0].ir, p[1])

def p_primary_expression_error(p):
    '''primary_expression : LPAREN expression error'''

    print("Error: Missing ')' Paranthesis")

def p_constant(p):
    '''constant : I_CONSTANT
                | F_CONSTANT
                | CHAR_CONSTANT
                | enumeration_constant'''
    
    p[0] = Node("constant", [p[1]])
    p[0].lvalue = False
    p[0].rvalue = True

    IrGen.constant(p[0].ir, p[1])
    token_type = p.slice[1].type

    type_map = {
        "I_CONSTANT": "int",
        "F_CONSTANT": "float",
        "CHAR_CONSTANT": "char"
    }

    if token_type in type_map:
        constant_type = type_map[token_type]
        var_sym = SymbolEntry(str(p[1]), constant_type, "constant")
        symtab.add_symbol(var_sym)

        p[0].return_type = constant_type

    p[0].vars.append(str(p[1]))

def p_enumeration_constant(p):
    '''enumeration_constant : IDENTIFIER'''

    p[0] = Node("enumeration_constant", [p[1]])
    symbol_table.append((p[1] , "int"))

    var_sym = SymbolEntry(str(p[1]), "int", "enumerator")
    symtab.add_symbol(var_sym)

    p[0].return_type = "int"

def p_string(p):
    '''string : STRING_LITERAL'''
    p[0] = Node("string", [p[1]])
    string_sym = SymbolEntry(str(p[1]), type='*const char', kind='constant')
    symtab.add_symbol(string_sym)

    p[0].vars.append(p[1])
    p[0].lvalue = False
    p[0].rvalue = True
    p[0].return_type = "*const char"

def p_generic_selection(p):
    '''generic_selection : GENERIC LPAREN assignment_expression COMMA generic_assoc_list RPAREN '''
    p[0] = Node("generic_selection", [p[3], p[5]])

def p_generic_selection_error(p):
    '''generic_selection : GENERIC LPAREN assignment_expression COMMA generic_assoc_list error '''
    
    print("Error: Missing ')' Paranthesis")

def p_generic_assoc_list(p):
    '''generic_assoc_list : generic_association
                         | generic_assoc_list COMMA generic_association'''
    if len(p) == 2:
        p[0] = Node("generic_assoc_list", [p[1]])
    else:
        p[0] = Node("generic_assoc_list", [p[1], p[3]])

def p_generic_association(p):
    '''generic_association : type_name COLON assignment_expression
                          | DEFAULT COLON assignment_expression'''
    p[0] = Node("generic_association", [p[1], p[3]])

# Postfix expressions
def p_postfix_expression(p):
    '''postfix_expression : primary_expression
                         | postfix_expression LBRACKET expression RBRACKET
                         | postfix_expression LPAREN argument_expression_list RPAREN
                         | postfix_expression LPAREN RPAREN
                         | postfix_expression DOT IDENTIFIER
                         | postfix_expression PTR_OP IDENTIFIER
                         | postfix_expression INC_OP
                         | postfix_expression DEC_OP
                         | LPAREN type_name RPAREN LBRACE initializer_list RBRACE
                         | LPAREN type_name RPAREN LBRACE initializer_list COMMA RBRACE '''
    if len(p) == 2:
        p[0] = Node("postfix_expression", [p[1]])
        #IR
        if(len(p[0].vars)>0 and symtab.lookup(p[0].vars[0]) is not None):
            s=symtab.lookup(p[0].vars[0]).kind
            p[0].listup = list(map(int, re.findall(r'\d+', s)))
            p[0].listup=p[0].listup[1:]

    if len(p) == 3:
        p[0] = Node("postfix_expression", [p[1],p[2]])

        if isinstance(p[2], str):
            if p[2] == "++" or p[2] == "--":
                if get_label(p[1].return_type) != "int":
                    raise ValueError(f"{p[2]} operator is incompatible with the operand of type {p[1].return_type}")

                if p[1].lvalue is not True and p[1].rvalue is not False:
                    raise ValueError(f"Operator {p[2]} can only be applied to modifyable lvalues")

        p[0].return_type = p[1].return_type
        p[0].lvalue = False
        p[0].rvalue = True

        # IR
        IrGen.inc_dec(p[0].ir,p[1].ir,p[2],True)

    elif len(p) == 4 and p[2] == ".":
        p[0] = Node("postfix_expression", [p[1], p[3]])
        field_identifier = p[3]
        struct_object = p[0].vars[0]

        if symtab.search_struct(struct_object, field_identifier) is None:
            print(f"The identifier '{field_identifier}' does not exist in the struct {struct_object}")

        p[0].vars = [f"{struct_object}.{field_identifier}"]
        p[0].return_type = symtab.search_struct(struct_object, field_identifier)

        p[0].lvalue = True
        p[0].rvalue = False

    elif len(p) == 4 and p[2] == '->':
        p[0] = Node("postfix_expression", [p[1], p[3]])
        field_identifier = p[3]
        struct_object = p[0].vars[0]

        if symtab.search_struct(struct_object, field_identifier) is None:
            print(f"The identifier '{field_identifier}' does not exist in the struct {struct_object}")

        type = symtab.lookup(struct_object).type
        if "*" not in type or not ("struct" in type or "union" in type):
            raise TypeError(f"Arrow Operators are used on pointers to object of types structs or unions")

        p[0].vars = [f"{struct_object}.{field_identifier}"]
        p[0].return_type = symtab.search_struct(struct_object, field_identifier)

        p[0].lvalue = True
        p[0].rvalue = False

    elif len(p) == 4 and p[3] != ")":
        p[0] = Node("postfix_expression", [p[1], p[2], p[3]])

    elif len(p) == 4:
        p[0] = Node("postfix_expression", [p[1]])
        p[0].iscall = 1

    elif len(p) == 5:
        p[0] = Node("postfix_expression", [p[1], p[3]])

        if p[2] == '[':
            first_var = p[1].vars[0]
            if first_var[-1] == ']':
                braces_count = first_var.count("]")
                first_var = first_var[:-2 * braces_count]
            
            if symtab.lookup(first_var) is not None:
                kind = symtab.lookup(first_var).kind
                if "D-array" in kind:
                    first_var += "[]" * int(kind[0])

            d, r, clean_var = count_deref_ref(first_var)
            p[1].return_type = get_type_from_var(clean_var, d, r, symtab)

            for c in p[3].vars:
                if not(symtab.lookup(c).type == "int" and symtab.lookup(c).kind == "constant")and not(symtab.lookup(c).type == "int" and symtab.lookup(c).kind == "variable"):
                    raise TypeError("Array size must be an integer constant or integer variable")

            p[0].expression = p[1].expression + "[" + p[3].expression + "]"
            p[0].vars = p[1].vars
            p[0].vars[0] += "[]"

            #postfix_expression : postfix_expression LBRACKET expression RBRACKET
            p[0].listup=p[1].listup[1:]
            IrGen.call_array_position(p[0].ir,p[1].ir,p[3].ir,p[0].listup)

        if p[2] == '(':
            p[0].iscall = 1

        p[0].return_type = p[1].return_type

    elif len(p) == 7 or len(p) == 8:
        p[0] = Node("postfix_expression", [p[2], p[5]])
        p[0].isbraces = True

        # compound literals 
        p[0].return_type = p[2].return_type

    if len(p) == 5 and p[2] == "(" and len(p[0].vars) > 0:

        func_params = symtab.search_params(p[0].vars[0])
        argument_list = p[3].param_list
        
        argument_param_match(argument_list, func_params)
            
        p[0].vars = [p[0].vars[0]]
        p[0].return_type = p[1].return_type
        p[0].lvalue = False
        p[0].rvalue = True

        ret = symtab.lookup(p[1].vars[0]).type
        IrGen.function_call(p[0].ir, p[1].ir, p[3].ir,ret)

    if len(p) == 4 and p[2] == "(":
        func_params = symtab.search_params(p[0].vars[0])
        argument_list = []

        ret = symtab.lookup(p[0].vars[0]).type
        argument_param_match(argument_list, func_params)
        p[0].return_type = p[1].return_type
        p[0].lvalue = False
        p[0].rvalue = True

        IrGen.function_call(p[0].ir, p[1].ir,None,ret)

def p_postfix_expression_error_1(p):
    '''postfix_expression : LPAREN type_name error LBRACE initializer_list RBRACE
                         | LPAREN type_name error LBRACE initializer_list COMMA RBRACE '''

    print("Error: Missing ')' Paranthesis")

def p_postfix_expression_error_2(p):
    '''postfix_expression : postfix_expression LPAREN argument_expression_list error
                         | postfix_expression LPAREN error
                         | LPAREN type_name RPAREN LBRACE initializer_list error
                         | LPAREN type_name RPAREN LBRACE initializer_list COMMA error '''
    
    print("Error: Missing '}' Brace")

def p_argument_expression_list(p):
    '''argument_expression_list : assignment_expression
                               | argument_expression_list COMMA assignment_expression'''
    if len(p) == 2:
        p[0] = Node("argument_expression_list", [p[1]])
        p[0].param_list = [p[1].return_type]
        IrGen.parameter_init(p[0].ir, p[1].ir)
    else:
        p[0] = Node("argument_expression_list", [p[1], p[3]])
        p[0].param_list = p[1].param_list
        p[0].param_list.append(p[3].return_type)
        IrGen.argument_expression(p[0].ir, p[1].ir, p[3].ir)

# Unary expressions
def p_unary_expression(p):
    '''unary_expression : postfix_expression
                       | INC_OP unary_expression
                       | DEC_OP unary_expression
                       | unary_operator cast_expression
                       | SIZEOF unary_expression
                       | SIZEOF LPAREN type_name RPAREN
                       | ALIGNOF LPAREN type_name RPAREN '''
    if len(p) == 2:
        p[0] = Node("unary_expression", [p[1]])

        if len(p[1].vars):
            var = p[1].vars[0]
            if var[-1] != ']':
                if symtab.lookup(var) is not None and "1D-array" in symtab.lookup(var).kind:
                    p[0].return_type = "*" + p[1].return_type 
            else:
                braces_count = var.count("]")
                new_var = var[:-2 * braces_count]

                if symtab.lookup(new_var) is not None:
                    kind = symtab.lookup(new_var).kind
                    if "D-array" in kind:
                        if str(braces_count) != str(kind[0]):
                            raise Exception("Invalid array access")
                        
        if(len(p[0].vars)>0 and '[' in p[0].vars[0] and symtab.lookup(p[0].vars[0].split('[')[0]) is not None and "array" in symtab.lookup(p[0].vars[0].split('[')[0]).kind):
            IrGen.unary_array(p[0].ir,p[1].ir,p[0].vars[0].split('[')[0])

        p[0].lvalue = True
        p[0].rvalue = False

    elif len(p) == 3:
        p[0] = Node("unary_expression", [p[1], p[2]])
        p[0].return_type = p[2].return_type

        if isinstance(p[1], Node) and p[1].operator == '&':
            if p[2].lvalue is not True and p[2].rvalue is not False:
                raise TypeError("Operand for & operator should be an lvalue")
            
            p[0].is_address = True
            for i in range(0,len(p[0].vars)):
                p[0].vars[i] = '!' + p[0].vars[i]
            p[0].return_type = '*' + p[0].return_type

            if symtab.lookup(p[2].vars[0]):
                if symtab.lookup(p[2].vars[0]).kind in ('constant','enumerator') :
                    raise Exception("Cant bind addr to constant/enum type")

            p[0].lvalue = False                
            p[0].rvalue = True
 
        if isinstance(p[1], Node) and p[1].operator == '*':
            if p[2].lvalue is not True and p[2].rvalue is not False:
                raise TypeError("Operand for * operator should be an lvalue")
            
            for i in range(0,len(p[0].vars)):
                p[0].vars[i] = '@' + p[0].vars[i]

            if p[0].return_type is not None:
                if p[0].return_type[0] == '*':
                    p[0].return_type = p[0].return_type[1:]
                else:
                    raise Exception("invalid deref")
                
            p[0].lvalue = True
            p[0].rvalue = False
        
        if isinstance(p[1], Node) and p[1].operator == "~": 
            if get_label(p[2].return_type) != "int":
                raise ValueError(f"~ operation cannot be used on {p[2].return_type}")
            
        if isinstance(p[1], Node) and p[1].operator == '!':
            if get_label(p[2].return_type) != "int":
                raise ValueError(f"~ operation cannot be used on {p[2].return_type}")
            
            pass
            
        if isinstance(p[1], str):
            if p[1] == "++" or p[1] == "--":
                if get_label(p[2].return_type) != "int":
                    raise ValueError(f"{p[1]} operation cannot be used on {p[2].return_type}")
        # IR
        if p[1] == '++' or p[1] == '--':
            p[0].lvalue = False
            p[0].rvalue = True

            IrGen.inc_dec(p[0].ir, p[2].ir, p[1])
        elif p[1] != "sizeof":    
            IrGen.unary(p[0].ir, p[2].ir,p[1].operator)

    elif len(p) == 5:
        p[0] = Node("unary_expression", [p[1], p[3]])
        
    if p[1] == "sizeof":
        p[0].return_type = "unsigned int"

def p_unary_expression_error(p):
    '''unary_expression : SIZEOF LPAREN type_name error
                       | ALIGNOF LPAREN type_name error '''

    print("Error: Missing ')' Paranthesis")

def p_unary_operator(p):
    '''unary_operator : AND
                     | TIMES
                     | PLUS
                     | MINUS
                     | TILDE
                     | NOT '''
    p[0] = Node("unary_operator", [p[1]])
    p[0].operator = p[1]

# Cast expressions
def p_cast_expression(p):
    '''cast_expression : unary_expression
                      | LPAREN type_name RPAREN cast_expression'''
    if len(p) == 2:
        p[0] = Node("cast_expression", [p[1]])

    else:
        p[0] = Node("cast_expression", [p[2], p[4]])

        if not compatible_cast(p[2].return_type, p[4].return_type):
            raise Exception(f"Return type of expression {p[4].return_type} cannot be casted to {p[2].return_type}")

        p[0].return_type = p[2].return_type
        p[0].lvalue = False
        p[0].rvalue = True

def p_cast_expression_error(p):
    '''cast_expression : LPAREN type_name error cast_expression'''

    print("Error: Missing ')' Paranthesis")

# Binary operations
def p_multiplicative_expression(p):
    '''multiplicative_expression : cast_expression
                                 | multiplicative_expression TIMES cast_expression
                                 | multiplicative_expression DIVIDE cast_expression
                                 | multiplicative_expression MOD cast_expression'''
    if len(p) == 2:
        p[0] = Node("multiplicative_expression", [p[1]])

    else:
        p[0] = Node("multiplicative_expression", [p[1], p[2], p[3]])
        p[0].iscall = p[1].iscall + p[3].iscall

        # ISO C99: 6.5.5: 2: Each of the operands shall have arithmetic type. The operands of the % operator shall have integer type.
        if "*" in p[1].return_type or "*" in p[3].return_type:
            raise Exception(f"Invalid Operands of type {p[1].return_type} and {p[3].return_type} to the operator *")
        
        if isinstance(p[2], str) and p[2] == "%":
            if get_label(p[1].return_type) == "float" or get_label(p[3].return_type) == "float":
                raise ValueError(f"Floating type expressions incompatible with mod operation")

        d, r, var0 = count_deref_ref(p[1].vars[0])
        var_type = get_type_from_var(var0, d, r, symtab)
        check_vars_type(p[3].vars, var_type, p[2], symtab, True)

        if implicit_type_compatibility(p[1].return_type, p[3].return_type, True):
            raise Exception(f"Invalid Operands of type {p[1].return_type} and {p[3].return_type} to the operator +")

        if dominating_type(p[1].return_type, p[3].return_type):
            p[0].return_type = p[1].return_type
        else:
            p[0].return_type = p[3].return_type

        p[0].lvalue = False
        p[0].rvalue = True
        
    func_id = 0
    for v in p[0].vars:
        if symtab.lookup(v) is not None and symtab.lookup(v).kind == 'function':
            func_id += 1

    if func_id != p[0].iscall:
        raise Exception("Invalid Function Call")
    
    # IR
    if len(p) == 4:
        IrGen.arithmetic_expression(p[0].ir, p[1].ir, p[2], p[3].ir)

def p_additive_expression(p):
    '''additive_expression : multiplicative_expression
                           | additive_expression PLUS multiplicative_expression
                           | additive_expression MINUS multiplicative_expression'''
    if len(p) == 2:
        p[0] = Node("additive_expression", [p[1]])
    
    else:
        p[0] = Node("additive_expression", [p[1], p[2], p[3]])
        p[0].iscall = p[1].iscall + p[3].iscall

        if "*" in p[1].return_type or "*" in p[3].return_type:
            if p[2] == '+':
                # ISO C99: 6.5.6: 2: For addition, either both operands shall have arithmetic type, or one operand shall be a pointer to an object type and the other shall have integer type. (Incrementing is equivalent to adding 1
                if "*" in p[1].return_type and "*" in p[3].return_type:
                    raise Exception(f"Addition Operation is not allowed for pointer type operands: {p[1].return_type} | {p[3].return_type}")

                p[0].return_type = addition_compatibility(p[1].return_type, p[3].return_type)
                
            elif p[2] == '-':
                # ISO C99: 6.5.6: 3: For Subtraction, both operands have arithmetic type; both operands are pointers to qualified or unqualified versions of compatible object types; or the left operand is a pointer to an object type and the right operand has integer type.
                p[0].return_type = subtraction_compatibility(p[1].return_type, p[3].return_type)
            
        else:
            # compute the type of the first variable
            d, r, var0 = count_deref_ref(p[1].vars[0])
            var_type = get_type_from_var(var0, d, r, symtab)

            # check if all the variables in p[3] are compatible
            check_vars_type(p[3].vars, var_type, p[2], symtab, True)

            if implicit_type_compatibility(p[1].return_type, p[3].return_type, True):
                raise Exception(f"Invalid Operands of type {p[1].return_type} and {p[3].return_type} to the operator +")

            # to determine the return type
            if dominating_type(p[1].return_type, p[3].return_type):
                p[0].return_type = p[1].return_type
            else:
                p[0].return_type = p[3].return_type

        IrGen.arithmetic_expression(p[0].ir, p[1].ir, p[2], p[3].ir)

        p[0].lvalue = False
        p[0].rvalue = True
    
def p_shift_expression(p):
    '''shift_expression : additive_expression
                       | shift_expression LEFT_OP additive_expression
                       | shift_expression RIGHT_OP additive_expression'''
    if len(p) == 2:
        p[0] = Node("shift_expression", [p[1]])
    else:
        p[0] = Node("shift_expression", [p[1], p[2], p[3]])

        dtype1 = None
        if len(p[1].vars) > 0:
            d, r, var0 = count_deref_ref(p[1].vars[0])
            dtype1 = get_type_from_var(var0, d, r, symtab)

        check_vars_type(p[3].vars, dtype1, p[2], symtab, False)

        if "*" in p[1].return_type or "*" in p[3].return_type:
            raise Exception(f"Invalid Operands of type {p[1].return_type} and {p[3].return_type} to the operator +")

        if get_label(p[1].return_type) == "float" or get_label(p[3].return_type) == "float":
            raise ValueError(f"Floating type expressions incompatible with shift operations")

        if dominating_type(p[1].return_type, p[3].return_type):
            p[0].return_type = p[1].return_type
        else:
            p[0].return_type = p[3].return_type

        IrGen.arithmetic_expression(p[0].ir, p[1].ir, p[2] ,p[3].ir)

def p_relational_expression(p):
    '''relational_expression : shift_expression
                             | relational_expression LT shift_expression
                             | relational_expression GT shift_expression
                             | relational_expression LE_OP shift_expression
                             | relational_expression GE_OP shift_expression'''
    if len(p) == 2:
        p[0] = Node("relational_expression", [p[1]])
    else:
        p[0] = Node("relational_expression", [p[1], p[2], p[3]])
        # Validate that the symbols in the left and right operands have compatible types.
        validate_relational_operands(p[1].vars, p[3].vars, symtab, True)

        p[0].return_type = "int"

def p_equality_expression(p):
    '''equality_expression : relational_expression
                          | equality_expression EQ_OP relational_expression
                          | equality_expression NE_OP relational_expression'''
    if len(p) == 2:
        p[0] = Node("equality_expression", [p[1]])
    else:
        p[0] = Node("equality_expression", [p[1], p[2], p[3]])
        for var in p[1].vars:
            if symtab.lookup(var) == None:
                raise ValueError(f"No symbol '{var}' in the symbol table")
            
        dtype1 = None
        if len(p[1].vars) > 0:
            d, r, var0 = count_deref_ref(p[1].vars[0])
            dtype1 = get_type_from_var(var0, d, r, symtab)

        check_vars_type(p[3].vars, dtype1, p[2], symtab, True)

        p[0].return_type = "int"

def p_and_expression(p):
    '''and_expression : equality_expression
                     | and_expression AND equality_expression'''
    if len(p) == 2:
        p[0] = Node("and_expression", [p[1]])
    else:
        p[0] = Node("and_expression", [p[1], p[2], p[3]])

        dtype1 = None
        if len(p[1].vars) > 0:
            d, r, var0 = count_deref_ref(p[1].vars[0])
            dtype1 = get_type_from_var(var0, d, r, symtab)

        check_vars_type(p[3].vars, dtype1, p[2], symtab, False)

        if get_label(p[1].return_type) == "float" or get_label(p[3].return_type) == "float":
            raise ValueError(f"Floating type expressions incompatible with {p[2].operator} operator")

        if dominating_type(p[1].return_type, p[3].return_type):
            p[0].return_type = p[1].return_type
        else:
            p[0].return_type = p[3].return_type


    if len(p) == 4:
        IrGen.arithmetic_expression(p[0].ir, p[1].ir, p[2] ,p[3].ir)
        

def p_exclusive_or_expression(p):
    '''exclusive_or_expression : and_expression
                              | exclusive_or_expression XOR and_expression'''
    if len(p) == 2:
        p[0] = Node("exclusive_or_expression", [p[1]])
    else:
        p[0] = Node("exclusive_or_expression", [p[1], p[2], p[3]])

        dtype1 = None
        if len(p[1].vars) > 0:
            d, r, var0 = count_deref_ref(p[1].vars[0])
            dtype1 = get_type_from_var(var0, d, r, symtab)

        check_vars_type(p[3].vars, dtype1, p[2], symtab, False)

        if get_label(p[1].return_type) == "float" or get_label(p[3].return_type) == "float":
            raise ValueError(f"Floating type expressions incompatible with {p[2].operator} operator")

        if dominating_type(p[1].return_type, p[3].return_type):
            p[0].return_type = p[1].return_type
        else:
            p[0].return_type = p[3].return_type

        IrGen.arithmetic_expression(p[0].ir, p[1].ir, p[2] ,p[3].ir)

def p_inclusive_or_expression(p):
    '''inclusive_or_expression : exclusive_or_expression
                              | inclusive_or_expression OR exclusive_or_expression'''
    if len(p) == 2:
        p[0] = Node("inclusive_or_expression", [p[1]])
    else:
        p[0] = Node("inclusive_or_expression", [p[1], p[2], p[3]])

        dtype1 = None
        if len(p[1].vars) > 0:
            d, r, var0 = count_deref_ref(p[1].vars[0])
            dtype1 = get_type_from_var(var0, d, r, symtab)

        check_vars_type(p[3].vars, dtype1, p[2], symtab, False)

        if get_label(p[1].return_type) == "float" or get_label(p[3].return_type) == "float":
            raise ValueError(f"Floating type expressions incompatible with {p[2].operator} operator")

        if dominating_type(p[1].return_type, p[3].return_type):
            p[0].return_type = p[1].return_type
        else:
            p[0].return_type = p[3].return_type

        IrGen.arithmetic_expression(p[0].ir, p[1].ir, p[2] ,p[3].ir)

def p_logical_and_expression(p):
    '''logical_and_expression : inclusive_or_expression
                             | logical_and_expression AND_OP inclusive_or_expression'''
    if len(p) == 2:
        p[0] = Node("logical_and_expression", [p[1]])
    else:
        p[0] = Node("logical_and_expression", [p[1], p[2], p[3]])

        dtype1 = None
        if len(p[1].vars) > 0:
            d, r, var0 = count_deref_ref(p[1].vars[0])
            dtype1 = get_type_from_var(var0, d, r, symtab)

        check_vars_type(p[3].vars, dtype1, p[2], symtab, False)

        if get_label(p[1].return_type) == "float" or get_label(p[3].return_type) == "float":
            raise ValueError(f"Floating type expressions incompatible with {p[2].operator} operator")

        if dominating_type(p[1].return_type, p[3].return_type):
            p[0].return_type = p[1].return_type
        else:
            p[0].return_type = p[3].return_type


def p_logical_or_expression(p):
    '''logical_or_expression : logical_and_expression
                            | logical_or_expression OR_OP logical_and_expression'''
    if len(p) == 2:
        p[0] = Node("logical_or_expression", [p[1]])
    else:
        p[0] = Node("logical_or_expression", [p[1], p[2], p[3]])

        dtype1 = None
        if len(p[1].vars) > 0:
            d, r, var0 = count_deref_ref(p[1].vars[0])
            dtype1 = get_type_from_var(var0, d, r, symtab)

        check_vars_type(p[3].vars, dtype1, p[2], symtab, False)

        if get_label(p[1].return_type) == "float" or get_label(p[3].return_type) == "float":
            raise ValueError(f"Floating type expressions incompatible with {p[2].operator} operator")

        if dominating_type(p[1].return_type, p[3].return_type):
            p[0].return_type = p[1].return_type
        else:
            p[0].return_type = p[3].return_type


def p_conditional_expression(p):
    '''conditional_expression : logical_or_expression
                             | logical_or_expression QUESTION expression COLON conditional_expression'''
    if len(p) == 2:
        p[0] = Node("conditional_expression", [p[1]])
    else:
        p[0] = Node("conditional_expression", [p[1], p[3], p[5]])

        dtype1 = None
        if len(p[1].vars) > 0:
            d, r, var0 = count_deref_ref(p[1].vars[0])
            dtype1 = get_type_from_var(var0, d, r, symtab)

        if implicit_type_compatibility(p[3].return_type, p[5].return_type, True):
            raise Exception(f"Ternary operators require both types to be compatible. Incompatible return types supplied: {p[3].return_type} | {p[5].return_type}")

        if dominating_type(p[3].return_type, p[5].return_type):
            p[0].return_type = p[3].return_type
        else:
            p[0].return_type = p[5].return_type


def p_assignment_expression(p):
    '''assignment_expression : conditional_expression
                             | unary_expression assignment_operator assignment_expression'''
    if len(p) == 2:  
        p[0] = Node("assignment_expression", [p[1]])
        
    else:  
        p[0] = Node("assignment_expression", [p[1], p[2], p[3]])
        
        lhs = p[0].vars[0]
        brace_count = 0
        if lhs[-1] == ']':
            brace_count = lhs.count("]")
            lhs = lhs[:-2 * brace_count]

        if symtab.lookup(lhs) is not None:
            kind = symtab.lookup(lhs).kind
            if "D-array" in kind:
                if str(brace_count) != str(kind[0]):
                    raise Exception(f"Invalid array access")

        d, r, clean_lhs = count_deref_ref(p[0].vars[0])
        lhs_type = get_type_from_var(clean_lhs, d, r, symtab, kind_check=['variable', 'parameter', 'reference', '*D-array*'])

        if lhs_type.startswith("const "):
            raise TypeError(f"Cannot re-assign value to const variable")
        
        if (p[2].operator == "<<=" or 
            p[2].operator == ">>=" or 
            p[2].operator == "%=" or
            p[2].operator == "&=" or
            p[2].operator == "^=" or 
            p[2].operator == "|="):
            validate_assignment(trim_value(lhs_type, "const"), p[2].operator, p[3].vars, symtab, False, True)

        else:
            validate_assignment(trim_value(lhs_type, "const"), p[2].operator, p[3].vars, symtab, True, False)

        if(p[2].operator == '='):
            IrGen.assignment(p[0].ir, p[1].ir, p[3].ir,p[0].vars[0])
        else:
            IrGen.op_assign(p[0].ir, p[1].ir, p[3].ir, p[2].operator)

        p[0].is_address = False
        
    p[0].return_type = p[1].return_type
    # IR

def p_assignment_operator(p):
    '''assignment_operator : ASSIGN
                          | MUL_ASSIGN
                          | DIV_ASSIGN
                          | MOD_ASSIGN
                          | ADD_ASSIGN
                          | SUB_ASSIGN
                          | LEFT_ASSIGN
                          | RIGHT_ASSIGN
                          | AND_ASSIGN
                          | XOR_ASSIGN
                          | OR_ASSIGN'''
    p[0] = Node("assignment_operator", [p[1]])
    p[0].operator = p[1]

def p_expression(p):
    '''expression : assignment_expression
                 | expression COMMA assignment_expression'''
    if len(p) == 2:
        p[0] = Node("expression", [p[1]])
    else:
        p[0] = Node("expression", [p[1], p[3]])

def p_constant_expression(p):
    '''constant_expression : conditional_expression'''
    p[0] = Node("constant_expression", [p[1]])

# Declarations
def p_declaration(p):
    '''declaration : declaration_specifiers SEMICOLON
                  | declaration_specifiers init_declarator_list SEMICOLON
                  | static_assert_declaration
                  | declaration_specifiers AND IDENTIFIER SEMICOLON'''
    # AST node creation
    if len(p) == 4:
        p[0] = Node("declaration", [p[1], p[2]])
        # IR
        p[0].ir = copy.deepcopy(p[2].ir)
    else:
        p[0] = Node("declaration", [p[1]])

    global datatypeslhs
    if len(datatypeslhs) > 0 and datatypeslhs[0] == "typedef":
        for var in p[0].vars:
            typedef_names.add(str(var))
    datatypeslhs = []

def p_declaration_error(p):
    '''declaration : declaration_specifiers error
                  | declaration_specifiers init_declarator_list error'''
    
    print("Error: Missing Semicolon")

def p_declaration_specifiers(p):
    '''declaration_specifiers : storage_class_specifier
                              | storage_class_specifier declaration_specifiers
                              | type_specifier
                              | type_specifier declaration_specifiers
                              | type_qualifier
                              | type_qualifier declaration_specifiers
                              | function_specifier
                              | function_specifier declaration_specifiers
                              | alignment_specifier
                              | alignment_specifier declaration_specifiers'''
    if len(p) == 3:
        p[0] = Node("declaration_specifiers", [p[1],p[2]])
    else:
        p[0] = Node("declaration_specifiers", [p[1]])

    global datatypeslhs
    datatypeslhs = p[0].dtypes

def p_storage_class_specifier(p):
    '''storage_class_specifier : TYPEDEF
	                            | EXTERN
	                            | STATIC
	                            | THREAD_LOCAL
	                            | AUTO
	                            | REGISTER'''
    p[0] = Node("storage_class_specifier", [p[1]])
    p[0].dtypes.append(str(p[1]))

def p_init_declarator_list(p):
    '''init_declarator_list : init_declarator
                           | init_declarator_list COMMA init_declarator'''
    p[0] = Node("init_declarator_list", [p[1], p[3]] if len(p) == 4 else [p[1]])
    
    if len(datatypeslhs)>0:
        datatypeslhs[0]=datatypeslhs[0].lstrip('*')
    if len(p) == 4:
        IrGen.multiple_assignment(p[0].ir, p[1].ir, p[3].ir)

def p_init_declarator(p):
    '''init_declarator : declarator ASSIGN initializer
                       | declarator'''
    
    global datatypeslhs
    base_type = ''

    if len(p) == 4: 
        p[0] = Node("init_declarator", [p[1], p[2], p[3]])
        abcd = 0
        for dtype in p[1].fdtypes:
            base_type += dtype
            base_type += " "
            abcd += 1
        base_type = base_type[:-1]

    else:
        p[0] = Node("init_declarator", [p[1]])
        abcd = 0
        for dtype in datatypeslhs:
            base_type += dtype
            base_type += " "
            abcd += 1
        base_type = base_type[:-1]

    validate_c_datatype(base_type, symtab)
    base_var = p[0].vars[0]

    kind="variable"
    if base_type.split(" ")[0] == "typedef" and len(base_type.split(" ")) >= 1:
        name = base_type.split(" ")[-1]
        kind=f"{name}"
        base_type=f"{name}"

    if isinstance(base_var, str) and base_var[0] == '%':
        if len(p[0].rhs) != 1:
            raise Exception("invalid reference created") 
        
        if symtab.lookup(p[0].rhs[0]).kind == 'constant':
            raise Exception("references can't be bound to constants")
        
        var_sym = SymbolEntry(
            name=str(base_var[1:]),
            type=str(base_type),
            kind="reference",
            refsto= p[0].rhs[0]
        )
        symtab.add_symbol(var_sym)

    elif symtab.lookup(base_var) is None:
        var_sym = SymbolEntry(
            name=str(base_var),
            type=str(base_type),
            kind=str(kind)
        )
        symtab.add_symbol(var_sym)
    
    elif symtab.lookup(base_var).kind != "function":
        var_sym = SymbolEntry(
            name=str(base_var),
            type=str(base_type),
            kind=str(kind)
        )
        symtab.add_symbol(var_sym)
    
    else:
        if symtab.current_scope != symtab.lookup(base_var).node:
            var_sym = SymbolEntry(
                name=str(base_var),
                type=str(base_type),
                kind=str(kind)
            )
            symtab.add_symbol(var_sym)

    if len(p) == 4:
        checkfunc = not p[3].iscall

        if p[0].isbraces:
            if base_var[-1] == ']':
                for rhs_var in p[0].rhs:
                    deref_count, ref_count, rhs_var = count_deref_ref(rhs_var)
                    type_ = get_type_from_var(rhs_var, deref_count, ref_count, symtab)

                    if symtab.lookup(rhs_var) is not None and implicit_type_compatibility(base_type, type_, True):
                        raise TypeError(f"Type mismatch in declaration of {p[0].vars[0]} because of {rhs_var}\n| base_type = {base_type} |\n| rhs_type = {type_} |")
                    
                    if checkfunc and symtab.lookup(rhs_var) is not None and symtab.lookup(rhs_var).kind == 'function':
                        raise Exception("Can't assign value of function")

            elif ((("struct" in base_type or "union" in base_type) or
            (symtab.lookup(base_type.split(' ')[-1]) is not None and 
            ("struct" in symtab.lookup(base_type.split(' ')[-1]).type or 
             "union" in symtab.lookup(base_type.split(' ')[-1]).type)))):
                struct_name = base_type.split(' ')[-1]
                struct_scope = symtab.lookup(struct_name).child
                struct_entries = struct_scope.entries

                if len(struct_entries) < len(p[0].rhs):
                    raise Exception("Number of identifiers in struct doesnt match with initialiser list length")
                
                if p[3].return_type is not None and strict_compatibility(base_type, p[3].return_type):
                    raise Exception(f"Cannot case the compound literal of type {p[3].return_type} to {base_type}")

                for struct_entry, list_entry in zip(struct_entries, p[0].rhs):
                    deref_count, ref_count, clean_list_entry = count_deref_ref(list_entry)
                    struct_entry_type = struct_entry.type

                    field_type = get_type_from_var(clean_list_entry, deref_count, ref_count, symtab)
        
                    if implicit_type_compatibility(struct_entry_type, field_type, True):
                        raise Exception(f"Type mismatch in {struct_entry_type} with provided {field_type}")
            else:
                notarray = (p[3].return_type == array_type_decay(p[3].return_type))
                            
                if notarray:
                    if implicit_type_compatibility(base_type, p[3].return_type, True):
                        raise Exception(f"Incompatible types {base_type} and {p[3].return_type}")
                    ## check all implicit type compatibility for rhs var

                    for rhs_var in p[0].rhs:
                        deref_count, ref_count, rhs_var = count_deref_ref(rhs_var)
                        type_ = get_type_from_var(rhs_var, deref_count, ref_count, symtab)

                        if implicit_type_compatibility(p[3].return_type, type_, True):
                            raise Exception(f"Type mismatch in {p[3].return_type} with provided {type_}")

                else:
                    if p[3].return_type is None:
                        p[3].return_type = base_type
                    if implicit_type_compatibility(base_type, array_type_decay(p[3].return_type), True):
                        raise Exception(f"Incompatible types {base_type} and {p[3].return_type}")

                    ## check all implicit type compatibility for rhs var

                    for rhs_var in p[0].rhs:
                        deref_count, ref_count, rhs_var = count_deref_ref(rhs_var)
                        type_ = get_type_from_var(rhs_var, deref_count, ref_count, symtab)

                        if implicit_type_compatibility(array_base_type(p[3].return_type), type_, True):
                            raise Exception(f"Type mismatch in {array_base_type(p[3].return_type)} with provided {type_}")


        else:
            if base_var[-1] == "]":
                raise Exception("Array being initialised without braces")
        
            elif ((("struct" in base_type or "union" in base_type) or
            (symtab.lookup(base_type.split(' ')[-1]) is not None and 
            ("struct" in symtab.lookup(base_type.split(' ')[-1]).type or 
             "union" in symtab.lookup(base_type.split(' ')[-1]).type)))):
                if len(p[0].rhs) > 1:
                    raise Exception("more than one variables in the rhs")
                
                if len(p[0].rhs) == 1:
                    deref_count, ref_count, rhs_var = count_deref_ref(p[0].rhs[0])
                    rhs_var_type = get_type_from_var(rhs_var, deref_count, ref_count, symtab)

                    if implicit_type_compatibility(base_type, rhs_var_type):
                        raise Exception(f"Type mismatch in {base_type} with provided {rhs_var_type}")
        
            else:
                type_ = p[3].return_type
                        
                if not (trim_value(base_type, "const").split(" ")[0] == "enum" and type_ == "int"):
                    if implicit_type_compatibility(base_type, type_, True):
                        raise TypeError(f"Type mismatch in declaration of {p[0].vars[0]}\n| base_type = {base_type} |\n| rhs_type = {type_} |")
            
        IrGen.assignment(p[0].ir, p[1].ir, p[3].ir,p[0].vars[0])

    p[0].is_address = False


def p_init_declarator_error(p):
    '''init_declarator : declarator error initializer'''

    print("Error: Expected '=' in Declaration Statement")

# Type specifiers
def p_type_specifier(p):
    '''type_specifier : VOID
                     | CHAR
                     | SHORT
                     | INT
                     | LONG
                     | FLOAT
                     | DOUBLE
                     | SIGNED
                     | UNSIGNED
                     | BOOL
                     | COMPLEX
                     | IMAGINARY
                     | atomic_type_specifier
                     | struct_or_union_specifier
                     | enum_specifier
                     | TYPEDEF_NAME'''
    p[0] = Node("type_specifier", [p[1]])
    if isinstance(p[1],str):
        p[0].return_type = p[1]
    else:
        p[0].return_type = p[1].return_type
    if not isinstance(p[1],Node):
        p[0].dtypes.append(p[1])
    
# Structures and Unions
def p_struct_or_union_specifier(p):
    '''struct_or_union_specifier : struct_or_union LBRACE enter_scope struct_declaration_list exit_scope RBRACE
                                | struct_or_union IDENTIFIER LBRACE enter_scope struct_declaration_list exit_scope RBRACE
                                | struct_or_union IDENTIFIER'''
    if len(p) == 7:
        p[0] = Node("struct_or_union_specifier", [p[1], p[4]])

    elif len(p) == 8:
        p[0] = Node("struct_or_union_specifier", [p[1], p[2], p[5]])
        symbol_table.append((p[2], str(p[1].children[0])))
        
        struct_name = p[2]
        sym_scope_level = symtab.current_scope_level - 1
        struct_sym = SymbolEntry(
            name=str(struct_name),
            type=f"{p[0].dtypes[0]}",
            kind=f"{p[0].dtypes[0]}"
        )

        symtab.add_symbol(struct_sym)

    else:
        p[0] = Node("struct_or_union_specifier", [p[1], p[2]])

        p[0].dtypes.append(p[2])
        p[0].return_type = p[1].return_type + " " + p[2]

def p_struct_or_union(p):
    '''struct_or_union : STRUCT
                      | UNION'''
    p[0] = Node("struct_or_union", [p[1]])
    p[0].return_type = p[1]
    p[0].dtypes.append(p[1])
    
def p_struct_declaration_list(p):
    '''struct_declaration_list : struct_declaration
                              | struct_declaration_list struct_declaration'''
    if len(p) == 2:
        p[0] = Node("struct_declaration_list", [p[1]])
    else:
        p[0] = Node("struct_declaration_list", [p[1], p[2]])

    p[0].dtypes = []
    p[0].vars = []
    
def p_struct_declaration(p):
    '''struct_declaration : specifier_qualifier_list SEMICOLON
                         | specifier_qualifier_list struct_declarator_list SEMICOLON
                         | static_assert_declaration'''
    if len(p) == 4:
        p[0] = Node("struct_declaration", [p[1], p[2]])
    else:
        p[0] = Node("struct_declaration", [p[1]])
    table_entry(p[0])

    if len(p) == 4:  # Has init_declarator_list
        base_type = ''
        for dtype in p[0].dtypes:
            base_type += dtype
            base_type += " "
        base_type = base_type[:-1]
        for decl in p[0].vars:  # Assume init_declarator_list is parsed
            var_sym = SymbolEntry(
                name=str(decl),
                type=str(base_type),
                kind="variable"
            )
            symtab.add_symbol(var_sym)

def p_struct_declaration_error(p):
    '''struct_declaration : specifier_qualifier_list error
                        | specifier_qualifier_list struct_declarator_list error'''

    print(f"Error: Missing Semicolon")

# Enums
def p_specifier_qualifier_list(p):
    '''specifier_qualifier_list : type_specifier specifier_qualifier_list
	                            | type_specifier
	                            | type_qualifier specifier_qualifier_list
                                | type_qualifier '''
    if len(p) == 2:
        p[0] = Node("specifier_qualifier_list", [p[1]])
        p[0].return_type = p[1].return_type
    else:
        p[0] = Node("specifier_qualifier_list", [p[1], p[2]])
        p[0].return_type = pretty_type_concat(p[1].return_type, p[2].return_type)
    
    global datatypeslhs
    datatypeslhs=p[0].dtypes

    
def p_struct_declarator_list(p):
    '''struct_declarator_list : struct_declarator
	                          | struct_declarator_list COMMA struct_declarator'''
    if len(p) == 2:
        p[0] = Node("struct_declarator_list", [p[1]])
    else:
        p[0] = Node("struct_declarator_list", [p[1], p[3]])
    
def p_struct_declarator(p):
    '''struct_declarator : COLON constant_expression
	                     | declarator COLON constant_expression
	                     | declarator'''
    if len(p) == 2:
        p[0] = Node("struct_declarator", [p[1]])
    elif len(p) == 4:
        p[0] = Node("struct_declarator", [p[1], p[3]])
    
def p_enum_specifier(p):
    '''enum_specifier : ENUM LBRACE enumerator_list RBRACE
                     | ENUM LBRACE enumerator_list COMMA RBRACE
                     | ENUM IDENTIFIER LBRACE enumerator_list RBRACE
                     | ENUM IDENTIFIER LBRACE enumerator_list COMMA RBRACE
                     | ENUM IDENTIFIER'''
    if len(p) == 3:
        p[0] = Node("enum_specifier", [p[2]])
        p[0].dtypes.append(p[1]+" "+p[2])
        if symtab.lookup(p[2])==None:
            raise Exception(f"Error: Enum Identifier {p[2]} not found")
    elif len(p) == 6 and p[3] == '{':
        p[0] = Node("enum_specifier", [p[2], p[4]])
    elif len(p) == 6:
        p[0] = Node("enum_specifier", [p[3]])
    elif len(p) == 7:
        p[0] = Node("enum_specifier", [p[2], p[4]])
    else:
        p[0] = Node("enum_specifier", [p[3]])

    if p[2]!='{':
        var_sym = SymbolEntry(
                name=str(p[2]),
                type="enum decl",
                kind="enum type"
            )
        symtab.add_symbol(var_sym)
    
    # symbol_table.append((p[2],p[1])) idk old intention toh hataaya
    
def p_enum_specifier_error(p):
    '''enum_specifier : ENUM LBRACE enumerator_list error
                     | ENUM LBRACE enumerator_list COMMA error
                     | ENUM IDENTIFIER LBRACE enumerator_list error
                     | ENUM IDENTIFIER LBRACE enumerator_list COMMA error'''

    print("Error: Missing '}' Brace")

def p_enumerator_list(p):
    '''enumerator_list : enumerator
                      | enumerator_list COMMA enumerator'''
    if len(p) == 2:
        p[0] = Node("enumerator_list", [p[1]])
    else:
        p[0] = Node("enumerator_list", [p[1], p[3]])
    
def p_enumerator(p):
    '''enumerator : enumeration_constant ASSIGN constant_expression
                 | enumeration_constant'''
    if len(p) == 4:
        p[0] = Node("enumerator", [p[1], p[3]])
    else:
        p[0] = Node("enumerator", [p[1]])
    
# Atomic types
def p_atomic_type_specifier(p):
    '''atomic_type_specifier : ATOMIC LPAREN type_name RPAREN '''
    p[0] = Node("atomic_type_specifier", [p[2]])
    
def p_atomic_type_specifier_error(p):
    '''atomic_type_specifier : ATOMIC LPAREN type_name error '''

    print("Error: Missing ')' Paranthesis")

# Type qualifiers
def p_type_qualifier(p):
    '''type_qualifier : CONST
                     | RESTRICT
                     | VOLATILE
                     | ATOMIC'''
    p[0] = Node("type_qualifier", [p[1]])
    p[0].return_type = p[1]
    p[0].dtypes.append("const")
    p[0].is_const = 1
    
# Function specifiers
def p_function_specifier(p):
    '''function_specifier : INLINE
                         | NORETURN'''
    p[0] = Node("function_specifier", [p[1]])
    
# Alignment specifiers
def p_alignment_specifier(p):
    '''alignment_specifier : ALIGNAS LPAREN type_name RPAREN
                          | ALIGNAS LPAREN constant_expression RPAREN '''
    if len(p) == 4:
        p[0] = Node("alignment_specifier", [p[2], p[3]])
    else:
        p[0] = Node("alignment_specifier", [p[2]])
    
def p_alignment_specifier_error(p):
    '''alignment_specifier : ALIGNAS LPAREN type_name error
                          | ALIGNAS LPAREN constant_expression error '''
    
    print("Error: Missing ')' Paranthesis")

# Declarators
def p_declarator(p):
    '''declarator : pointer direct_declarator
                 | direct_declarator'''
    if len(p) == 3:
        p[0] = Node("declarator", [p[1], p[2]])
        # Pointer ka fix
        c = 0
        if symtab.lookup(p[0].vars[0]):
            t = symtab.lookup(p[0].vars[0]).type
            for z in t:
                if z == '*':
                    c+=1
                else:
                    break

        p[0].vars[0] = '#'*p[0].is_const + p[0].vars[0] + '?'*c
        p[0].is_const = 0
    else:
        p[0] = Node("declarator", [p[1]])

    datatypeslhs = []
    

def p_direct_declarator(p):
    '''direct_declarator : IDENTIFIER
                        | LPAREN declarator RPAREN 
                        | direct_declarator LBRACKET RBRACKET
                        | direct_declarator LBRACKET TIMES RBRACKET
                        | direct_declarator LBRACKET STATIC type_qualifier_list assignment_expression RBRACKET
                        | direct_declarator LBRACKET STATIC assignment_expression RBRACKET
                        | direct_declarator LBRACKET type_qualifier_list TIMES RBRACKET
                        | direct_declarator LBRACKET type_qualifier_list STATIC assignment_expression RBRACKET
                        | direct_declarator LBRACKET type_qualifier_list assignment_expression RBRACKET
                        | direct_declarator LBRACKET type_qualifier_list RBRACKET
                        | direct_declarator LBRACKET assignment_expression RBRACKET
                        | direct_declarator LPAREN parameter_type_list RPAREN
                        | direct_declarator LPAREN RPAREN
                        | direct_declarator LPAREN identifier_list RPAREN
                        | AND IDENTIFIER
                        '''
    # IDENTIFIER case
    if len(p) == 2:
        p[0] = Node("direct_declarator", [p[1]])
        p[0].vars.append(p[1])
        # IR
        IrGen.identifier(p[0].ir, p[1])
    elif len(p) == 3:
        #REF
        p[0] = Node("direct_declarator",[p[1],p[2]])
        t = '%' + p[2]
        p[0].vars.append(t)
    # LPAREN declarator RPAREN case
    elif len(p) == 4 and p[1] == '(':
        p[0] = Node("direct_declarator", [p[2]])
    
    # direct_declarator LBRACKET RBRACKET case
    elif len(p) == 4 and p[2] == '[':
        p[0] = Node("array_declarator", [p[1]])
        p[0].vars[0] += "[" + "]"
    
    # direct_declarator LBRACKET TIMES RBRACKET case
    elif len(p) == 5 and p[2] == '[' and p[3] == '*':
        p[0] = Node("vla_declarator", [p[1]])
    
    # direct_declarator LBRACKET assignment_expression RBRACKET case
    elif len(p) == 5 and p[2] == '[' and p[3] != '*':
        for c in p[3].vars:
            if not(symtab.lookup(c).type == "int" and symtab.lookup(c).kind == "constant")and not(symtab.lookup(c).type == "int" and symtab.lookup(c).kind == "variable"):
                raise TypeError("Array size must be an integer constant or integer variable")
        p[3].vars = []
        
        p[0] = Node("array_declarator", [p[1], p[3]])
        p[0].vars[0] += "[" + p[3].expression + "]"
    
    # direct_declarator LPAREN RPAREN case
    elif len(p) == 4 and p[2] == '(' and p[3] == ')':
        p[0] = Node("function_declarator", [p[1]])
    
    # direct_declarator LPAREN parameter_type_list RPAREN or identifier_list case
    elif len(p) == 5 and p[2] == '(':
        p[0] = Node("function_declarator", [p[1], p[3]])
    
    # direct_declarator LBRACKET type_qualifier_list RBRACKET case
    elif len(p) == 5 and p[2] == '[' and p[3] != '*':
        p[0] = Node("qualified_array_declarator", [p[1], p[3]])
    
    # direct_declarator LBRACKET STATIC assignment_expression RBRACKET case
    elif len(p) == 6 and p[2] == '[' and p[3] == 'static':
        p[0] = Node("static_array_declarator", [p[1], p[4]])
    
    # direct_declarator LBRACKET type_qualifier_list TIMES RBRACKET case
    elif len(p) == 6 and p[2] == '[' and p[4] == '*':
        p[0] = Node("qualified_vla_declarator", [p[1], p[3]])
    
    # direct_declarator LBRACKET type_qualifier_list assignment_expression RBRACKET case
    elif len(p) == 6 and p[2] == '[' and p[4] != '*':
        p[0] = Node("qualified_array_declarator", [p[1], p[3], p[4]])
    
    # direct_declarator LBRACKET STATIC type_qualifier_list assignment_expression RBRACKET case
    elif len(p) == 7 and p[3] == 'static':
        p[0] = Node("static_qualified_array_declarator", [p[1], p[4], p[5]])
    
    # direct_declarator LBRACKET type_qualifier_list STATIC assignment_expression RBRACKET case
    elif len(p) == 7 and p[4] == 'static':
        p[0] = Node("qualified_static_array_declarator", [p[1], p[3], p[5]])

    if len(p) == 2 or len(p) == 3:
        base_type = ''
        for dtype in datatypeslhs:
            base_type += dtype
            base_type += " "
        base_type = base_type[:-1]
        p[0].fdtypes=datatypeslhs
        validate_c_datatype(base_type, symtab)

    if len(p) > 2 and p[2] == '(':
        func_name = p[1].vars[0] #check gang
        base_type = ''
        for dtype in p[1].fdtypes:
            base_type += dtype
            base_type += " "
        
        base_type=base_type[:-1]
        # Add function to GLOBAL scope
        func_sym = SymbolEntry(
            name=str(func_name),
            type=str(base_type),  # Return type from declaration_specifiers
            kind="function"
        )

        symtab.add_function_symbol(func_sym)

def p_direct_declarator_error(p):
    '''direct_declarator : LPAREN declarator error
                        | direct_declarator LPAREN parameter_type_list error
                        | direct_declarator LPAREN error
                        | direct_declarator LPAREN identifier_list error '''

    print("Error: Missing ')' Paranthesis")

# Pointers
def p_pointer(p):
    '''pointer : TIMES type_qualifier_list pointer
              | TIMES type_qualifier_list
              | TIMES pointer
              | TIMES '''
    if len(p) == 4:
        p[0] = Node("pointer", [p[1],p[2],p[3]])
        p[0].return_type = pretty_type_concat(p[1].return_type, p[2].return_type, p[3].return_type)
    elif len(p) == 2:
        p[0] = Node("pointer", [p[1]])
        p[0].return_type = "*"
    else:
        p[0] = Node("pointer", [p[1], p[2]])
        p[0].return_type = pretty_type_concat(p[1], p[2].return_type)
        if "const" in p[0].dtypes:
            p[0].dtypes.remove("const")
    datatypeslhs[0] = '*' + datatypeslhs[0]

def p_type_qualifier_list(p):
    '''type_qualifier_list : type_qualifier
                          | type_qualifier_list type_qualifier'''
    if len(p) == 2:
        p[0] = Node("type_qualifier_list", [p[1]])
        p[0].return_type = p[1].return_type
    else:
        p[0] = Node("type_qualifier_list", [p[1], p[2]])
        p[0].return_type = pretty_type_concat(p[1].return_type, p[2].return_type)
    
# Parameters
def p_parameter_type_list(p):
    '''parameter_type_list : parameter_list COMMA ELLIPSIS
                          | parameter_list'''
    if len(p) == 2:
        p[0] = Node("parameter_type_list", [p[1]])
    else:
        p[0] = Node("parameter_type_list", [p[1], p[3]])
        param_sym = SymbolEntry(
            name='_VAR_ARGS_', #check gang
            type=str('...'),
            kind=str("parameter"),
            isForwardable=True
        )
        symtab.add_symbol(param_sym)
    
def p_parameter_list(p):
    '''parameter_list : parameter_declaration
                     | parameter_list COMMA parameter_declaration'''
    if len(p) == 2:
        p[0] = Node("parameter_list", [p[1]])
    else:
        p[0] = Node("parameter_list", [p[1], p[3]])
    
def p_parameter_declaration(p):
    '''parameter_declaration : declaration_specifiers declarator
                            | declaration_specifiers abstract_declarator
                            | declaration_specifiers'''
    # AST node creation
    if len(p) == 2:
        p[0] = Node("parameter_declaration", [p[1]])
    elif len(p) == 3:
        p[0] = Node("parameter_declaration", [p[1], p[2]])

    # -- Symbol Table Handling (only for concrete declarators) --
        if len(p) > 2 and hasattr(p[2], 'name'):
            base_type = ''
            for dtype in p[0].dtypes:
                base_type += dtype
                base_type += " "
            base_type = base_type[:-1]
            param_sym = SymbolEntry(
                name=str(p[0].vars[0]), #check gang
                type=str(base_type),
                kind="parameter",
                isForwardable=True
            )
            symtab.add_symbol(param_sym)   

            ## if you dont do this it forwards this up and in init_declarator you end up adding all the params again to global scope 
            ## for test case run this on function definition 
            ## at init_declarator, we have already cleared out all the params and pushed them in the function scope, we dont need the params to forward up to the parent anyway
            p[0].vars = [] 

def p_identifier_list(p):
    '''identifier_list : IDENTIFIER
                      | identifier_list COMMA IDENTIFIER'''
    if len(p) == 2:
        p[0] = Node("identifier_list", [p[1]])
    else:
        p[0] = Node("identifier_list", [p[1], p[3]])
    
# Type names
def p_type_name(p):
    '''type_name : specifier_qualifier_list abstract_declarator
                | specifier_qualifier_list'''
    if len(p) == 2:
        p[0] = Node("type_name", [p[1]])
        p[0].return_type = p[1].return_type
    else:
        p[0] = Node("type_name", [p[1], p[2]])
        p[0].return_type = pretty_type_concat(p[1].return_type, p[2].return_type)
    p[0].dtypes = []
    
# Abstract declarators
def p_abstract_declarator(p):
    '''abstract_declarator : pointer direct_abstract_declarator
                          | pointer
                          | direct_abstract_declarator'''
    if len(p) == 2:
        p[0] = Node("abstract_declarator", [p[1]])
        p[0].return_type = p[1].return_type
    else:
        p[0] = Node("abstract_declarator", [p[1], p[2]])
        p[0].return_type = pretty_type_concat(p[1].return_type, p[2].return_type)
    
def p_direct_abstract_declarator(p):
    '''direct_abstract_declarator : LPAREN abstract_declarator RPAREN
                                 | LBRACKET RBRACKET
                                 | LBRACKET TIMES RBRACKET
                                 | LBRACKET STATIC type_qualifier_list assignment_expression RBRACKET
                                 | LBRACKET STATIC assignment_expression RBRACKET
                                 | LBRACKET type_qualifier_list STATIC assignment_expression RBRACKET
                                 | LBRACKET type_qualifier_list assignment_expression RBRACKET
                                 | LBRACKET type_qualifier_list RBRACKET
                                 | LBRACKET assignment_expression RBRACKET
                                 | direct_abstract_declarator LBRACKET RBRACKET
                                 | direct_abstract_declarator LBRACKET TIMES RBRACKET
                                 | direct_abstract_declarator LBRACKET STATIC type_qualifier_list assignment_expression RBRACKET
                                 | direct_abstract_declarator LBRACKET STATIC assignment_expression RBRACKET
                                 | direct_abstract_declarator LBRACKET type_qualifier_list assignment_expression RBRACKET
                                 | direct_abstract_declarator LBRACKET type_qualifier_list STATIC assignment_expression RBRACKET
                                 | direct_abstract_declarator LBRACKET type_qualifier_list RBRACKET
                                 | direct_abstract_declarator LBRACKET assignment_expression RBRACKET
                                 | LPAREN RPAREN
                                 | LPAREN parameter_type_list RPAREN
                                 | direct_abstract_declarator LPAREN RPAREN
                                 | direct_abstract_declarator LPAREN parameter_type_list RPAREN'''
    
    if len(p) == 4 and p[1] == '(' and p[3] == ')':
        p[0] = Node("direct_abstract_declarator", [p[2]])
    elif len(p) == 3 and p[1] == '[' and p[2] == ']':
        p[0] = Node("direct_abstract_declarator", [])
        p[0].return_type = "[]"
    elif len(p) == 3 and p[1] == '[' and p[2] == 'static':
        p[0] = Node("direct_abstract_declarator", [p[1], p[2], p[3]])
    else:
        p[0] = Node("direct_abstract_declarator", [p[1], p[2]])

def p_direct_abstract_declarator_error(p):
    '''direct_abstract_declarator : LPAREN abstract_declarator error
                                 | LPAREN error
                                 | LPAREN parameter_type_list error
                                 | direct_abstract_declarator LPAREN error
                                 | direct_abstract_declarator LPAREN parameter_type_list error'''
    
    print("Error: Missing ')' Paranthesis")

# Initialization
def p_initializer(p):
    '''initializer : LBRACE initializer_list RBRACE
                   | LBRACE initializer_list COMMA RBRACE
                   | LBRACE RBRACE
                   | assignment_expression'''
    if len(p) == 4 or len(p) == 5:  
        p[0] = Node("initializer", [p[2]])  
        p[0].isbraces = True
    else:  
        p[0] = Node("initializer", [p[1]])  
    
    # for c in p[0].vars:
    #     deref_count, ref_count, clean_var = count_deref_ref(c)
    #     type_ = get_type_from_var(clean_var, deref_count, ref_count, symtab)

    #     if type_ is None:
    #         raise Exception(f"Error: variable {clean_var} not declared")
        
    p[0].rhs += p[0].vars
    p[0].vars = []


def p_initializer_error(p):
    '''initializer : LBRACE initializer_list error
                   | LBRACE initializer_list COMMA error'''

    print("Error: Missing '}' Brace")


def p_initializer_list(p):
    '''initializer_list : designation initializer
                       | initializer
                       | initializer_list COMMA designation initializer
                       | initializer_list COMMA initializer'''
    if len(p) == 2:
        p[0] = Node("initializer_list", [p[1]])
    elif len(p) == 4:
        p[0] = Node("initializer_list", [p[1], p[3]])
    else:
        p[0] = Node("initializer_list", [p[1], p[3]])
    
    p[0].return_type = None


def p_designation(p):
    '''designation : designator_list ASSIGN '''
    p[0] = Node("designation", [p[1]])


def p_designator_list(p):
    '''designator_list : designator
                      | designator_list designator'''
    if len(p) == 2:
        p[0] = Node("designator_list", [p[1]])
    else:
        p[0] = Node("designator_list", [p[1], p[2]])


def p_designator(p):
    '''designator : LBRACKET constant_expression RBRACKET
                 | DOT IDENTIFIER'''
    if len(p) == 4:
        p[0] = Node("designator", [p[2]])
    elif len(p) == 3:
        p[0] = Node("designator", [p[1], p[2]])


# Static assertions
def p_static_assert_declaration(p):
    '''static_assert_declaration : STATIC_ASSERT LPAREN constant_expression COMMA STRING_LITERAL RPAREN SEMICOLON'''
    p[0] = Node("static_assert_declaration", [p[3], p[5]])

def p_static_assert_declaration_error_1(p):
    '''static_assert_declaration : STATIC_ASSERT LPAREN constant_expression COMMA STRING_LITERAL RPAREN error'''

    print("Error: Missing Semicolon")
        
def p_static_assert_declaration_error_2(p):
    '''static_assert_declaration : STATIC_ASSERT LPAREN constant_expression COMMA STRING_LITERAL error SEMICOLON'''

    print("Error: Missing ')' Paranthesis")

def p_static_assert_declaration_error_3(p):
    '''static_assert_declaration : STATIC_ASSERT error constant_expression COMMA STRING_LITERAL RPAREN SEMICOLON'''

    print("Error: Missing '(' Paranthesis")

# Statements
def p_statement(p):
    '''statement : labeled_statement
                | compound_statement
                | expression_statement
                | selection_statement
                | iteration_statement
                | jump_statement'''
    p[0] = Node("statement", [p[1]])


def p_labeled_statement(p):
    '''labeled_statement : IDENTIFIER COLON
                        | CASE constant_expression COLON statement
                        | DEFAULT COLON statement'''
    if len(p) == 3 and p[2] == ':' and p[1] != 'default':
        p[0] = Node("labeled_statement", [p[1]])
        # IR
        IrGen.label_add(p[0].ir,p[1])
    elif len(p) == 5 and p[1] == 'case':
        p[0] = Node("labeled_statement", [p[1], p[2], p[4]])
    elif len(p) == 4:
        p[0] = Node("labeled_statement", [p[1], p[3]])


def p_compound_statement(p):
    '''compound_statement : LBRACE RBRACE
                          | LBRACE enter_scope block_item_list exit_scope RBRACE'''
    # Handle empty block
    if len(p) == 3:
        symtab.enter_scope()    # Enter new scope
        symtab.exit_scope()     # Exit immediately for empty block
        p[0] = Node("compound_statement", [])
    # Handle block with content
    else:
        p[0] = Node("compound_statement", [p[3]])  # p[3] = block_item_list

def p_function_compound_statement(p):
    '''function_compound_statement : LBRACE RBRACE
                          | LBRACE function_enter_scope block_item_list function_exit_scope RBRACE'''
    # Handle empty block
    if len(p) == 3:
        symtab.function_enter_scope()    # Enter new scope
        symtab.function_exit_scope()     # Exit immediately for empty block
        p[0] = Node("compound_statement", [])
    # Handle block with content
    else:
        p[0] = Node("compound_statement", [p[3]])  # p[3] = block_item_list

# Mid-rule action helpers
def p_enter_scope(p):
    'enter_scope :'
    symtab.enter_scope()

def p_function_enter_scope(p):
    'function_enter_scope :'
    symtab.function_enter_scope()

def p_exit_scope(p):
    'exit_scope :'
    symtab.exit_scope()

def p_function_exit_scope(p):
    'function_exit_scope :'
    symtab.function_exit_scope()

def p_compound_statement_error(p):
    '''compound_statement : LBRACE error
                         | LBRACE enter_scope block_item_list exit_scope error '''

    print("Error: Missing '}' Brace")

def p_block_item_list(p):
    '''block_item_list : block_item
                      | block_item_list block_item'''
    if len(p) == 2:
        p[0] = Node("block_item_list", [p[1]])
    else:
        p[0] = Node("block_item_list", [p[1], p[2]])
        IrGen.blockitem(p[0].ir, p[1].ir, p[2].ir)


def p_block_item(p):
    '''block_item : declaration
                 | statement'''
    p[0] = Node("block_item", [p[1]])


def p_expression_statement(p):
    '''expression_statement : SEMICOLON
                           | expression SEMICOLON '''
    if len(p) == 2:
        p[0] = Node("expression_statement", [])
    else:
        p[0] = Node("expression_statement", [p[1]])

def p_expression_statement_error(p):
    '''expression_statement : error
                           | expression error'''
    
    print("Error: Missing Semicolon")


def p_selection_statement(p):
    '''selection_statement : IF LPAREN expression RPAREN statement ELSE statement
                          | IF LPAREN expression RPAREN statement
                          | SWITCH LPAREN expression RPAREN statement'''
    if len(p) == 8:
        p[0] = Node("selection_statement", [p[1], p[3], p[5], p[6], p[7]])
    elif len(p) == 6:
        p[0] = Node("selection_statement", [p[1], p[3], p[5]])

def p_selection_statement_error(p):
    '''selection_statement : IF LPAREN expression error statement ELSE statement
                          | IF LPAREN expression error statement
                          | SWITCH LPAREN expression error statement'''
    
    print("Error: Missing ')' Paranthesis")


def p_iteration_statement(p):
    '''iteration_statement : WHILE LPAREN expression RPAREN statement
                          | DO statement WHILE LPAREN expression RPAREN SEMICOLON
                          | DO statement UNTIL LPAREN expression RPAREN SEMICOLON
                          | FOR LPAREN enter_scope expression_statement expression_statement RPAREN statement exit_scope
                          | FOR LPAREN enter_scope expression_statement expression_statement expression RPAREN statement exit_scope
                          | FOR LPAREN enter_scope declaration expression_statement RPAREN statement exit_scope
                          | FOR LPAREN enter_scope declaration expression_statement expression RPAREN statement exit_scope'''
    # p[0] = Node("iteration_statement", [p[2], p[4]])
    # While loop vale
    if p[1] == "while":
        p[0] = Node("iteration_statement", [p[1], p[3],p[5]])
        IrGen.while_loop(p[0].ir, p[3].ir, p[5].ir)
    # Do while loop vale
    elif p[1] == 'do':
        p[0] = Node("iteration_statement", [p[1],p[2],p[3],p[5]])
        if p[3] == 'while':
            IrGen.do_while_loop(p[0].ir, p[5].ir, p[2].ir)
        elif p[3] == 'until':
            IrGen.do_until_loop(p[0].ir, p[5].ir, p[2].ir)
    # For loop vale
    elif p[1] == 'for':
        if len(p) == 9:
            p[0] = Node("iteration_statement", [p[1], p[4], p[5],p[7]])
        else:
            p[0] = Node("iteration_statement", [p[1], p[4], p[5],p[6],p[8]])

def p_jump_statement(p):
    '''jump_statement : GOTO IDENTIFIER SEMICOLON
                     | CONTINUE SEMICOLON
                     | BREAK SEMICOLON
                     | RETURN SEMICOLON
                     | RETURN expression SEMICOLON'''
    global returns
    if len(p) == 3:
        p[0] = Node("jump_statement", [p[1]])
        if p[1] =='return':
            returns.add('void')
    elif len(p) == 4:
        p[0] = Node("jump_statement", [p[1], p[2]])
        if p[1] == 'return':
            returns.add(p[2].return_type)
            IrGen.return_jump(p[0].ir,p[2].ir)
        if p[1] == 'goto':
            IrGen.goto_label(p[0].ir,p[2])


def p_jump_statement_error(p):
    '''jump_statement : GOTO IDENTIFIER error
                     | CONTINUE error
                     | BREAK error
                     | RETURN error
                     | RETURN expression error'''
    
    print("Error: Missing Semicolon")

# Function definitions
def p_function_definition(p):
    '''function_definition : declaration_specifiers declarator declaration_list function_compound_statement
                           | declaration_specifiers declarator function_compound_statement'''
    # Create AST node
    if len(p) == 5:
        p[0] = Node("function_definition", [p[1], p[2], p[3], p[4]])
    else:
        p[0] = Node("function_definition", [p[1], p[2], p[3]])
        IrGen.function_definition(p[0].ir, p[2].ir, p[3].ir,p[2].vars[0])

    ## because child scope was created earlier and attached already.
    symtab.to_add_child = False
    symtab.the_child = None

    # -- Symbol Table Handling --
    # Get function name from declarator (assume p[2] has 'name' attribute)
    func_name = p[2].vars[0] #check gang
    base_type = ''
    for dtype in p[1].dtypes:
        base_type += dtype
        base_type += " "
    
    base_type=base_type[:-1]


    global returns
    while len(func_name) > 0 and func_name[-1] == '?':
        func_name = func_name[:-1]
    b_type = symtab.lookup(func_name).type

    # if len(returns) > 1:
    #     raise Exception("Multiple Return Types")

    for type in returns:
        if implicit_type_compatibility(b_type, type, True):
            raise Exception("Invalid Type of Value returned")
    returns = set()
    # Enter FUNCTION SCOPE (for parameters/local vars)
    # symtab.enter_scope(func_name)
    # symtab.exit_scope()

def p_declaration_list(p):
    '''declaration_list : declaration
	                    | declaration_list declaration'''
    if len(p) == 2:
        p[0] = Node("declaration_list", [p[1]])
    else:
        p[0] = Node("declaration_list", [p[1], p[2]])

lines = ""
input_text = ""

def find_column(input_str, token):
    """Compute the column number of a token (1-indexed)."""
    last_newline = input_str.rfind('\n', 0, token.lexpos)
    if last_newline < 0:
        last_newline = -1
    return token.lexpos - last_newline

def p_error(p):
    if not p:
        print("========================================")
        print("SYNTAX ERROR:")
        print("Error: Right Braces '}' mismatch")
        print("========================================")
        return 

    col = find_column(input_text, p)

    print("========================================")
    print("SYNTAX ERROR:")
    print(f"  At line {p.lineno}, column {col}")
    print(f"  Unexpected token: {p.type} ('{p.value}')")
    print("----------------------------------------")

    error_line = lines[p.lineno - 1] if p.lineno - 1 < len(lines) else ""
    print(error_line)

    pointer = " " * (col - 1) + "^"
    print(pointer)
    exit(0)
    
# Build parser
parser = yacc.yacc(debug=True)

def parseFile(filename, ogfilename, treedir, symtabdir,graphgen=False,irgen=True):
    global IrGen
    IrGen = IRGenerator(irgen)
    IrGen.set_out_file(ogfilename)
    
    with open(filename, 'r') as file:
        data = file.read()

    pretty_print_box(data, "File Contents")
    print(f"Parsing file: {filename}\n")

    root = parser.parse(data)

    pretty_print_header("Final Symbol Table", text_style="bold underline red")
    print(symtab)

    if graphgen:
        treepath = os.path.join(treedir, ogfilename[:-2])
        symtabpath = os.path.join(symtabdir, ogfilename[:-2])
        graph = root.to_graph()
        graph.render(treepath, format='png', cleanup=True)
        print(f"Parse tree saved as renderedTrees/{ogfilename[:-2]}.png")
        graph = symtab.to_graph()
        graph.render(symtabpath, format='png', cleanup=True)
        print(f"Symbol table tree saved as renderedSymbolTables/{ogfilename[:-2]}.png")

    print("\n")

    symtab.clear()
    typedef_names.clear()
    lexer.lineno = 0