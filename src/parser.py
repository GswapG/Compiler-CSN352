import ply.yacc as yacc
import os
from tokens import tokens  # Assuming you have a matching lexer
from sys import argv
from ply import yacc
from utils import *
from lexer import *
from tree import *
from symtab_new import *
# from ir_codegen import parseTree_to_3AC

## pip3 install pycryptodome 
from Crypto.Hash import SHA256
import uuid

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
        while(isinstance(var,str) and var[-1]=='$'):
            stars += "*"
            var = var[:-1]
        while(isinstance(var,str) and var[0]=='#'):
            consts += " const"
            var = var[1:]
        symbol_table.append((var,compound_dtype+stars+consts))
    if compound_dtype.split(" ")[0] == "typedef":
        for var in node.vars:
            typedef_names.add(str(var))

# Translation Unit
def p_translation_unit(p):
    '''translation_unit : external_declaration
                       | translation_unit external_declaration'''
    if len(p) == 2:
        p[0] = Node("translation_unit", [p[1]])
    else:
        p[0] = Node("translation_unit", [p[1], p[2]])

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

def p_primary_expression_identifier(p):
    '''primary_expression : IDENTIFIER'''

    p[0] = Node("primary_expression", [p[1]])
    p[0].vars.append(str(p[1]))
    c1 = 0
    c2 = 0
    cpy = p[1]
    
    while isinstance(cpy, str) and cpy[0] == '@':
        c1 += 1
        cpy = cpy[1:]

    check = symtab.lookup(cpy)
    if check != None:
        p[0].dtypes = check.type
        p[0].return_type = check.type

def p_primary_expression_error(p):
    '''primary_expression : LPAREN expression error'''

    print("Error: Missing ')' Paranthesis")


def p_constant(p):
    '''constant : I_CONSTANT
                | F_CONSTANT
                | CHAR_CONSTANT
                | enumeration_constant'''
    p[0] = Node("constant", [p[1]])  # Include the constant value
    token_type = p.slice[1].type
    if token_type == "I_CONSTANT":
        var_sym = SymbolEntry(
                name=str(p[1]),
                type="int",
                kind="constant"
            )
        symtab.add_symbol(var_sym)
        p[0].return_type = 'int'
    elif token_type == "F_CONSTANT":
        var_sym = SymbolEntry(
                name=str(p[1]),
                type="float",
                kind="constant"
            )
        symtab.add_symbol(var_sym)
        p[0].return_type = 'float'
    elif token_type == "CHAR_CONSTANT":
        var_sym = SymbolEntry(
                name=str(p[1]),
                type="char",
                kind="constant"
            )
        symtab.add_symbol(var_sym)
        p[0].return_type = 'char'
    p[0].vars.append(str(p[1]))


def p_enumeration_constant(p):
    '''enumeration_constant : IDENTIFIER'''

    p[0] = Node("enumeration_constant", [p[1]])
    symbol_table.append((p[1] , "int"))

    var_sym = SymbolEntry(
                name=str(p[1]),
                type="int",
                kind="enumerator"
            )
    symtab.add_symbol(var_sym)

def p_string(p):
    '''string : STRING_LITERAL'''
    p[0] = Node("string", [p[1]])
    symtab.add_symbol(SymbolEntry(
        name=str(p[1]),
        type='*char',
        kind='constant'
    ))

    p[0].vars.append(p[1])
    p[0].return_type = '*char'

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
    if len(p) == 3:
        p[0] = Node("postfix_expression", [p[1],p[2]])

        if isinstance(p[2], str):
            if p[2] == "++" or p[2] == "--":
                if get_label(p[1].return_type) == "float":
                    raise ValueError(f"{p[2]} operator is incompatible with floating point values")

    elif len(p) == 4 and p[2] == ".":
        p[0] = Node("postfix_expression", [p[1], p[3]])

    elif len(p) == 4 and p[3] != ")":
        p[0] = Node("postfix_expression", [p[1], p[2], p[3]])

    elif len(p) == 4:
        p[0] = Node("postfix_expression", [p[1]])
        p[0].iscall = 1
        #here

    elif len(p) == 5:
        if p[2] == '[':
            for i in range(0,len(p[1].vars)):
                p[1].vars[i] = '@' + p[1].vars[i]
            # if p[1].return_type is not None:
            #     if p[1].return_type[0] == '*':
            #         p[0].return_type = p[1].return_type[1:]
            #     else:
            #         raise Exception("invalid deref")
        p[0] = Node("postfix_expression", [p[1], p[3]])
        if p[2] == '(':
            p[0].iscall = 1

    elif len(p) == 7:
        p[0] = Node("postfix_expression", [p[2], p[5]])
    elif len(p) == 8:
        p[0] = Node("postfix_expression", [p[2], p[5]])

    if len(p) == 4 and p[2] == ".":
        identifier = p[3]
        variable_identifier = str(p[0].vars[0]).split(" ")[-1]
        variable = symtab.lookup(variable_identifier)

        struct_name = str(variable.type).rstrip(" ").split(" ")[-1]
        struct_table = symtab.lookup(struct_name)
        struct_scope = struct_table.child

        # checking if the identifier exists in the struct 
        exists = False
        for entry in struct_scope.entries:
            if entry.name == identifier:
                exists = True

        if not exists:
            print(f"The identifier '{identifier}' does not exist in the struct {struct_name}")

        p[0].vars = [f"{struct_name} {variable.name} {identifier}"]

    if len(p) == 5 and p[2] == "(" and len(p[0].vars) > 0:
        print(p[0].vars)

        func_params = symtab.search_params(p[0].vars[0])
        argument_list = p[3].param_list
        
        argument_param_match(argument_list, func_params)
            
        p[0].vars = [p[0].vars[0]]
        p[0].return_type = p[1].return_type

    if len(p) == 4 and p[2] == "(":
        func_params = symtab.search_params(p[0].vars[0])
        argument_list = []

        argument_param_match(argument_list, func_params)

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
    else:
        p[0] = Node("argument_expression_list", [p[1], p[3]])
        p[0].param_list = p[1].param_list
        p[0].param_list.append(p[3].return_type)

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
        p[0].return_type = p[1].return_type

    elif len(p) == 3:
        p[0] = Node("unary_expression", [p[1], p[2]])
        p[0].return_type = p[2].return_type

        if isinstance(p[1], Node) and p[1].children[0].type == '&':
            p[0].is_address = True
            for i in range(0,len(p[0].vars)):
                p[0].vars[i] = '!' + p[0].vars[i]
            p[0].return_type = '*' + p[0].return_type
            if symtab.lookup(p[2].vars[0]):
                if symtab.lookup(p[2].vars[0]).kind in ('constant','enumerator') :
                    raise Exception("Cant bind addr to constant/enum type")
 
        if isinstance(p[1], Node) and p[1].children[0].type == '*':
            for i in range(0,len(p[0].vars)):
                p[0].vars[i] = '@' + p[0].vars[i]
            if p[0].return_type is not None:
                if p[0].return_type[0] == '*':
                    p[0].return_type = p[0].return_type[1:]
                else:
                    raise Exception("invalid deref")
        
        if isinstance(p[1], Node) and p[1].operator == "~": 
            if get_label(p[2].return_type) == "float":
                raise ValueError("~ operation cannot be used on floating point values")
            
        if isinstance(p[1], str):
            if p[1] == "++" or p[1] == "--":
                if get_label(p[2].return_type) == "float":
                    raise ValueError(f"{p[1]} operation cannot be used on floating point values")

    elif len(p) == 5:
        p[0] = Node("unary_expression", [p[1], p[3]])

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
        p[0].return_type = p[1].return_type
    else:
        p[0] = Node("cast_expression", [p[2], p[4]])

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

    # Process first operand to get expected type (dtype1)
    dtype1 = None
    if len(p[1].vars) > 0:
        d, r, var0 = count_deref_ref(p[1].vars[0])
        dtype1 = get_type_from_var(var0, d, r, symtab)

    # Check that each variable in the first operand has the expected type
    check_vars_type(p[1].vars, dtype1, "multiplicative", symtab, True)

    if len(p) == 4:
        check_vars_type(p[3].vars, dtype1, p[2], symtab, True)

        if isinstance(p[2], str) and p[2] == "%":
            if get_label(p[1].return_type) == "float" or get_label(p[3].return_type) == "float":
                raise ValueError(f"Floating type expressions incompatible with mod operation")

    # Additional function call validation:
    func_id = 0
    for v in p[0].vars:
        if symtab.lookup(v) is not None and symtab.lookup(v).kind == 'function':
            func_id += 1

    if func_id != p[0].iscall:
        raise Exception("Invalid Function Call")
    
    if len(p) == 4:
        if dominating_type(p[1].return_type, p[3].return_type):
            p[0].return_type = p[1].return_type
        else:
            p[0].return_type = p[3].return_type

    p[0].return_type = p[1].return_type

def p_additive_expression(p):
    '''additive_expression : multiplicative_expression
                           | additive_expression PLUS multiplicative_expression
                           | additive_expression MINUS multiplicative_expression'''
    if len(p) == 2:
        p[0] = Node("additive_expression", [p[1]])
    else:
        p[0] = Node("additive_expression", [p[1], p[2], p[3]])
        p[0].iscall = p[1].iscall + p[3].iscall

    dtype1 = None
    if len(p[1].vars) > 0:
        d, r, var0 = count_deref_ref(p[1].vars[0])
        dtype1 = get_type_from_var(var0, d, r, symtab)

    # Check that each variable in the first operand has the expected type
    check_vars_type(p[1].vars, dtype1, "addition", symtab, True)

    if len(p) == 4:
        check_vars_type(p[3].vars, dtype1, p[2], symtab, True)

        if dominating_type(p[1].return_type, p[3].return_type):
            p[0].return_type = p[1].return_type
        else:
            p[0].return_type = p[3].return_type
    p[0].return_type = p[1].return_type
    
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

    if len(p) == 4:
        check_vars_type(p[3].vars, dtype1, p[2], symtab, False)

        if get_label(p[1].return_type) == "float" or get_label(p[3].return_type) == "float":
            raise ValueError(f"Floating type expressions incompatible with shift operations")

        if dominating_type(p[1].return_type, p[3].return_type):
            p[0].return_type = p[1].return_type
        else:
            p[0].return_type = p[3].return_type

    p[0].return_type = p[1].return_type


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

    if len(p) == 4:
        check_vars_type(p[3].vars, dtype1, p[2], symtab, True)


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

    if len(p) == 4:
        check_vars_type(p[3].vars, dtype1, p[2], symtab, False)

        if get_label(p[1].return_type) == "float" or get_label(p[3].return_type) == "float":
            raise ValueError(f"Floating type expressions incompatible with {p[2].operator} operator")

        if dominating_type(p[1].return_type, p[3].return_type):
            p[0].return_type = p[1].return_type
        else:
            p[0].return_type = p[3].return_type

    p[0].return_type = p[1].return_type
        

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

    if len(p) == 4:
        check_vars_type(p[3].vars, dtype1, p[2], symtab, False)

        if get_label(p[1].return_type) == "float" or get_label(p[3].return_type) == "float":
            raise ValueError(f"Floating type expressions incompatible with {p[2].operator} operator")

        if dominating_type(p[1].return_type, p[3].return_type):
            p[0].return_type = p[1].return_type
        else:
            p[0].return_type = p[3].return_type

    p[0].return_type = p[1].return_type

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

    if len(p) == 4:
        check_vars_type(p[3].vars, dtype1, p[2], symtab, False)

        if get_label(p[1].return_type) == "float" or get_label(p[3].return_type) == "float":
            raise ValueError(f"Floating type expressions incompatible with {p[2].operator} operator")

        if dominating_type(p[1].return_type, p[3].return_type):
            p[0].return_type = p[1].return_type
        else:
            p[0].return_type = p[3].return_type

    p[0].return_type = p[1].return_type

def p_logical_and_expression(p):
    '''logical_and_expression : inclusive_or_expression
                             | logical_and_expression AND_OP inclusive_or_expression'''
    if len(p) == 2:
        p[0] = Node("logical_and_expression", [p[1]])
    else:
        p[0] = Node("logical_and_expression", [p[1], p[2], p[3]])

def p_logical_or_expression(p):
    '''logical_or_expression : logical_and_expression
                            | logical_or_expression OR_OP logical_and_expression'''
    if len(p) == 2:
        p[0] = Node("logical_or_expression", [p[1]])
    else:
        p[0] = Node("logical_or_expression", [p[1], p[2], p[3]])

def p_conditional_expression(p):
    '''conditional_expression : logical_or_expression
                             | logical_or_expression QUESTION expression COLON conditional_expression'''
    if len(p) == 2:
        p[0] = Node("conditional_expression", [p[1]])
    else:
        p[0] = Node("conditional_expression", [p[1], p[3], p[5]])

def p_assignment_expression(p):
    '''assignment_expression : conditional_expression
                             | unary_expression assignment_operator assignment_expression'''
    if len(p) == 2:  
        p[0] = Node("assignment_expression", [p[1]])
    else:  
        p[0] = Node("assignment_expression", [p[1], p[2], p[3]])
        
        print(p[0].vars)
        lhs_raw = p[0].vars[0]
        if isinstance(lhs_raw, str) and ' ' in lhs_raw:
            lhs_entry = lookup_symbol(lhs_raw, symtab)
            lhs_effective_without_const = effective_type(lhs_entry, 0, 0, True)
            lhs_effective = effective_type(lhs_entry, 0, 0)

        else:
            d, r, clean_lhs = process_deref_ref(lhs_raw)
            lhs_entry = lookup_symbol(clean_lhs, symtab)
            lhs_effective_without_const = effective_type(lhs_entry, d, r, True)
            lhs_effective = effective_type(lhs_entry, d, r)

        if lhs_entry is None:
            raise Exception(f"identifier {lhs_raw} does not exist")
        
        if lhs_entry.kind not in ['variable', 'parameter']:
            raise TypeError("Value can only be assigned to variable/param types!")
        
        if (p[2].operator == "<<=" or 
            p[2].operator == ">>=" or 
            p[2].operator == "%=" or
            p[2].operator == "&=" or
            p[2].operator == "^=" or 
            p[2].operator == "|="):
            validate_assignment(lhs_entry, lhs_effective_without_const, p[2].operator, p[3].vars, symtab, False, True)

        else:
            validate_assignment(lhs_entry, lhs_effective_without_const, p[2].operator, p[3].vars, symtab, True, False)

        if lhs_effective.startswith("const "):
            raise TypeError(f"Cannot re-assign value to const variable '{lhs_entry.name}' of type '{lhs_entry.type}'")
        
        p[0].is_address = False

        
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

def validate_c_datatype(data_type):
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

    if tokens[0]=="struct":
        tokens = tokens[1:]
        for c in tokens:
            if c in allowed_keywords:
                raise ValueError(f"Invalid data type structure '{data_type}'.")
            else:
                return True

    abcd = symtab.lookup(tokens[0])
    if(abcd is not None and abcd.type == "struct"):
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

def p_init_declarator(p):
    '''init_declarator : declarator ASSIGN initializer
                       | declarator'''
    if len(p) == 4: 
        p[0] = Node("init_declarator", [p[1], p[2], p[3]])

    else:  # Case: declarator
        p[0] = Node("init_declarator", [p[1]])

    global datatypeslhs

    base_type = ''
    abcd = 0
    for dtype in p[1].fdtypes:
        base_type += dtype
        base_type += " "
        abcd += 1
    base_type = base_type[:-1]

    validate_c_datatype(base_type)

    for decl in p[0].vars:
        kind2="variable"

        if(base_type.split(" ")[0]=="typedef" and len(base_type.split(" ")) >= 1):
            name = base_type.split(" ")[-1]
            kind2=f"{name}"
            base_type=f"{name}"

        if isinstance(decl, str) and decl[0] == '%' :
            if len(p[0].rhs) != 1:
                raise Exception("invalid reference created") 
            if symtab.lookup(p[0].rhs[0]).kind == 'constant':
                raise Exception("references can't be bound to constants")
            var_sym = SymbolEntry(
                name=str(decl[1:]),
                type=str(base_type),
                kind="reference",
                refsto= p[0].rhs[0]
            )
            symtab.add_symbol(var_sym)

        elif symtab.lookup(decl) is None:
            var_sym = SymbolEntry(
                name=str(decl),
                type=str(base_type),
                kind=str(kind2)
            )
            print("OKAY IM CALLED")
            symtab.add_symbol(var_sym)
        
        elif symtab.lookup(decl).kind != "function":
            var_sym = SymbolEntry(
                name=str(decl),
                type=str(base_type),
                kind=str(kind2)
            )
            print("OKAY IM CALLED")
            symtab.add_symbol(var_sym)
            
    for var in p[0].rhs:
        if isinstance(var, str) and ' ' in var:
            name, _, identifier = var.split(' ')
            if symtab.search_struct(name, identifier) == None:
                raise ValueError(f"No symbol '{var}' in the symbol table")

            continue

        _, __, var = process_deref_ref(var)

        if symtab.lookup(var) == None:
            raise ValueError(f"No symbol '{var}' in the symbol table")
        
    var = p[0].vars[0]
    deref_count = 0
    ref_count = 0

    while isinstance(var, str):
        if var[-1] == '$':
            deref_count += 1
            var = var[:-1]
            
        ## we can support references here
        else:
            break
    while isinstance(var, str) and len(var) > 0:
        if var[0] == '%':
            var = var[1:]  # Remove '%'
        else:
            break 

    base = symtab.lookup(var).type
    base_no_const = base
    if "const " in base:
        base_no_const = trim_value(base_no_const, "const")
        # base_no_const = ' '.join(word for word in base_no_const.split() if word != "const")
    if "static " in base_no_const:
        base_no_const = ' '.join(word for word in base_no_const.split() if word != "static")
    checkfunc = True

    if len(p) == 4:
        checkfunc = not p[3].iscall

    ## struct or union
    if (symtab.lookup(base_no_const) is not None and (symtab.lookup(base_no_const).type == 'struct' or symtab.lookup(base_no_const).type == 'union')) or ('struct' in base_no_const or 'union' in base_no_const) and not base_no_const.startswith("*"):

        if p[0].isbraces:
            struct_name = base_no_const.split(' ')[-1]
            struct_scope = symtab.lookup(struct_name).child
            struct_entries = struct_scope.entries

            if len(struct_entries) < len(p[0].rhs):
                raise Exception("Number of identifiers in struct doesnt match with initialiser list length")

            for struct_entry, list_entry in zip(struct_entries, p[0].rhs):
                deref_count, ref_count, list_entry = count_deref_ref(list_entry)

                if isinstance(list_entry, str) and ' ' in list_entry:
                    name, identifier, field = list_entry.split(" ")

                    struct_entry_type = struct_entry.type
                    if "const " in struct_entry_type or "static " in struct_entry_type:
                        struct_entry_type = ' '.join(word for word in struct_entry_type.split() if word not in ["const", "static"]).rstrip(' ')
                    field_type = symtab.search_struct(name, field).type.rstrip(' ')

                    for i in range(0, deref_count):
                        if isinstance(field_type, str) and field_type[0] == '*':
                            field_type = field_type[1:]
                        else:
                            raise TypeError("Invalid Deref")
                    for j in range(0, ref_count):
                        if isinstance(field_type, str):
                            field_type = "*" + field_type  
                    
                    if struct_entry_type != field_type:
                        raise Exception(f"Type mismatch in {struct_entry_type} with provided {field_type}")
                
                else:
                    struct_entry_type = struct_entry.type.split("const ")[-1].rstrip(' ')
                    list_entry_type = symtab.lookup(list_entry).type.rstrip(' ')

                    for i in range(0, deref_count):
                        if list_entry_type[0] == '*':
                            list_entry_type = list_entry_type[1:]
                        else:
                            raise TypeError("Invalid Deref")
                        
                    for j in range(0, ref_count):
                        if isinstance(list_entry_type, str):
                            list_entry_type = "*" + list_entry_type 

                    if struct_entry_type != list_entry_type:
                        raise Exception(f"Type mismatch in {struct_entry_type} with provided {list_entry_type}")
        else:
            if len(p) > 2:
                if len(p[0].rhs) == 1:
                    deref_count, ref_count, rhs_var = count_deref_ref(p[0].rhs[0])

                    rhs_var = symtab.lookup(rhs_var)
                    rhs_var_type = rhs_var.type

                    for i in range(0, deref_count):
                        if isinstance(rhs_var_type, str) and rhs_var_type[0] == '*':
                            rhs_var_type = rhs_var_type[1:]
                        else:
                            raise TypeError("Invalid Deref")
                    for j in range(0, ref_count):
                        if isinstance(rhs_var_type, str):
                            rhs_var_type = "*" + rhs_var_type 

                    if base_no_const != rhs_var_type:
                        raise Exception(f"Type mismatch in {base_no_const} with provided {rhs_var_type}")
                elif len(p[0].rhs) > 1:
                    raise Exception("more than one variables in the rhs")

    ## other types
    else: 

        for rhs_var in p[0].rhs:

            deref_count, ref_count, rhs_var = count_deref_ref(rhs_var)
            type_ = get_type_from_var(rhs_var, deref_count, ref_count, symtab)

            array_check = base_no_const.lstrip('*')

            if p[0].isbraces:
                if symtab.lookup(rhs_var) is not None and array_check != (symtab.lookup(rhs_var)).type:
                    raise TypeError(f"Type mismatch in declaration of {p[0].vars[0]} because of {rhs_var}\n| base_type = {base} |\n| rhs_type = {(symtab.lookup(rhs_var)).type} |")
                
                if checkfunc and symtab.lookup(rhs_var) is not None and symtab.lookup(rhs_var).kind == 'function':
                    raise Exception("Can't assign value of function")
                
            else:
                if not (base_no_const.split(" ")[0] == "enum" and type_ == "int"):
                    if check_types(base, type_, True):
                        raise TypeError(f"Type mismatch in declaration of {p[0].vars[0]} because of {rhs_var}\n| base_type = {base} |\n| rhs_type = {type_} |")
            
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
    if not isinstance(p[1],Node):
        p[0].dtypes.append(p[1])
    pass

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




def p_struct_or_union(p):
    '''struct_or_union : STRUCT
                      | UNION'''
    p[0] = Node("struct_or_union", [p[1]])
    p[0].dtypes.append(p[1])
    pass

def p_struct_declaration_list(p):
    '''struct_declaration_list : struct_declaration
                              | struct_declaration_list struct_declaration'''
    if len(p) == 2:
        p[0] = Node("struct_declaration_list", [p[1]])
    else:
        p[0] = Node("struct_declaration_list", [p[1], p[2]])

    p[0].dtypes = []
    p[0].vars = []
    pass

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
    else:
        p[0] = Node("specifier_qualifier_list", [p[1], p[2]])
    #neelkumar
    global datatypeslhs
    datatypeslhs=p[0].dtypes
    pass

def p_struct_declarator_list(p):
    '''struct_declarator_list : struct_declarator
	                          | struct_declarator_list COMMA struct_declarator'''
    if len(p) == 2:
        p[0] = Node("struct_declarator_list", [p[1]])
    else:
        p[0] = Node("struct_declarator_list", [p[1], p[3]])
    pass

def p_struct_declarator(p):
    '''struct_declarator : COLON constant_expression
	                     | declarator COLON constant_expression
	                     | declarator'''
    if len(p) == 2:
        p[0] = Node("struct_declarator", [p[1]])
    elif len(p) == 4:
        p[0] = Node("struct_declarator", [p[1], p[3]])
    pass

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
            print(f"Error: Enum Identifier {p[2]} not found")
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
    pass

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
    pass

def p_enumerator(p):
    '''enumerator : enumeration_constant ASSIGN constant_expression
                 | enumeration_constant'''
    if len(p) == 4:
        p[0] = Node("enumerator", [p[1], p[3]])
    else:
        p[0] = Node("enumerator", [p[1]])
    pass

# Atomic types
def p_atomic_type_specifier(p):
    '''atomic_type_specifier : ATOMIC LPAREN type_name RPAREN '''
    p[0] = Node("atomic_type_specifier", [p[2]])
    pass

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
    p[0].dtypes.append("const")
    p[0].is_const = 1
    pass

# Function specifiers
def p_function_specifier(p):
    '''function_specifier : INLINE
                         | NORETURN'''
    p[0] = Node("function_specifier", [p[1]])
    pass

# Alignment specifiers
def p_alignment_specifier(p):
    '''alignment_specifier : ALIGNAS LPAREN type_name RPAREN
                          | ALIGNAS LPAREN constant_expression RPAREN '''
    if len(p) == 4:
        p[0] = Node("alignment_specifier", [p[2], p[3]])
    else:
        p[0] = Node("alignment_specifier", [p[2]])
    pass

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

        p[0].vars[0] = '#'*p[0].is_const + p[0].vars[0] + '$'*c
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
        p[0].vars[0] += "$"
    
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
        p[0].vars[0] += "$"        
    
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
        validate_c_datatype(base_type)

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

        # symtab.add_symbol(func_sym)
        symtab.add_symbol_and_create_child_scope(func_sym)
        # symtab.to_add_parent = True
        # symtab.the_parent = symtab.lookup(func_name) 

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
    elif len(p) == 2:
        p[0] = Node("pointer", [p[1]])
    else:
        p[0] = Node("pointer", [p[1], p[2]])
        if "const" in p[0].dtypes:
            p[0].dtypes.remove("const")
    datatypeslhs[0] = '*' + datatypeslhs[0]

def p_type_qualifier_list(p):
    '''type_qualifier_list : type_qualifier
                          | type_qualifier_list type_qualifier'''
    if len(p) == 2:
        p[0] = Node("type_qualifier_list", [p[1]])
    else:
        p[0] = Node("type_qualifier_list", [p[1], p[2]])
    pass

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
    pass

def p_parameter_list(p):
    '''parameter_list : parameter_declaration
                     | parameter_list COMMA parameter_declaration'''
    if len(p) == 2:
        p[0] = Node("parameter_list", [p[1]])
    else:
        p[0] = Node("parameter_list", [p[1], p[3]])
    pass

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
            print("hi")
            print(param_sym.name)
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
    pass

# Type names
def p_type_name(p):
    '''type_name : specifier_qualifier_list abstract_declarator
                | specifier_qualifier_list'''
    if len(p) == 2:
        p[0] = Node("type_name", [p[1]])
    else:
        p[0] = Node("type_name", [p[1], p[2]])
    p[0].dtypes = []
    pass

# Abstract declarators
def p_abstract_declarator(p):
    '''abstract_declarator : pointer direct_abstract_declarator
                          | pointer
                          | direct_abstract_declarator'''
    if len(p) == 2:
        p[0] = Node("abstract_declarator", [p[1]])
    else:
        p[0] = Node("abstract_declarator", [p[1], p[2]])
    pass

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
    elif len(p) == 2 and p[0] == '[' and p[1] == ']':
        p[0] = Node("direct_abstract_declarator", [])
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
    
    for c in p[0].vars:
        if symtab.lookup(c) is None:
            print(f"Error: variable {c} not declared")
    p[0].rhs += p[0].vars
    p[0].vars=[]


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
    '''labeled_statement : IDENTIFIER COLON statement
                        | CASE constant_expression COLON statement
                        | DEFAULT COLON statement'''
    if len(p) == 4 and p[2] == ':':
        p[0] = Node("labeled_statement", [p[1], p[3]])
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


# Mid-rule action helpers
def p_enter_scope(p):
    'enter_scope :'
    symtab.enter_scope()

def p_exit_scope(p):
    'exit_scope :'
    symtab.exit_scope()

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
    # Do while loop vale
    elif p[1] == 'do':
        p[0] = Node("iteration_statement", [p[1],p[2],p[3],p[5]])
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
            print(f"return type jump {p[2].return_type}")
            returns.add(p[2].return_type)


def p_jump_statement_error(p):
    '''jump_statement : GOTO IDENTIFIER error
                     | CONTINUE error
                     | BREAK error
                     | RETURN error
                     | RETURN expression error'''
    
    print("Error: Missing Semicolon")

# Function definitions
def p_function_definition(p):
    '''function_definition : declaration_specifiers declarator declaration_list compound_statement
                           | declaration_specifiers declarator compound_statement'''
    # Create AST node
    if len(p) == 5:
        p[0] = Node("function_definition", [p[1], p[2], p[3], p[4]])
    else:
        p[0] = Node("function_definition", [p[1], p[2], p[3]])

    # -- Symbol Table Handling --
    # Get function name from declarator (assume p[2] has 'name' attribute)
    func_name = p[2].vars[0] #check gang
    base_type = ''
    for dtype in p[1].dtypes:
        base_type += dtype
        base_type += " "
    
    base_type=base_type[:-1]


    global returns
    while len(func_name) > 0 and func_name[-1] == '$':
        func_name = func_name[:-1]
    b_type = symtab.lookup(func_name).type

    if len(returns) > 1:
        raise Exception("Multiple Return Types")

    for type in returns:
        if check_types(b_type, type, True):
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

current_filename = ""
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
    
def strip_file(file):
    lines = file.split('\n')
    new_file = ""
    for line in lines:
        new_file += line.strip()
    return new_file

# Build parser
parser = yacc.yacc()
strargv = [str(x) for x in argv]

testcase_hashes = []
stress_testing = './stress_testing/'
for filename in sorted(os.listdir(stress_testing)): 
    filepath = os.path.join(stress_testing, filename)
    if os.path.isfile(filepath):
        with open(filepath, 'r') as file:
            data = file.read()
        current_filename = filepath
        input_text = strip_file(data)

        hash = SHA256.new() 
        hash.update(input_text.encode())
        input_hash = hash.hexdigest()

        testcase_hashes.append(input_hash)

with open(f"./testcasehashes.txt", "w") as f:
    for hash in testcase_hashes:
        f.write(hash)
        f.write("\n")

    f.close()

stress_test_file = len(testcase_hashes)
testcases_dir = './tests/testing/'
if "-d" in strargv or "--directory" in strargv:
    position = 1 + (strargv.index("-d") if strargv.index("-d") != -1 else strargv.index("--directory"))
    if len(strargv) <= position:
        raise Exception("Incorrect use of the flag \"-d\" or \"--directory\". Please specify the directory path following the flag.")
    
    testcases_dir = strargv[position]

specific_filename = None
if "-f" in strargv or "--file" in strargv:
    position = 1 + (strargv.index("-f") if strargv.index("-f") != -1 else strargv.index("--file"))
    if len(strargv) <= position:
        raise Exception("Incorrect use of the flag \"-f\" or \"--file\". Please specify the directory path following the flag.")
    
    specific_filename = strargv[position]

def print_symbol_table(symtab):
    if not symtab:
        print("Symbol table is empty")
        return

    # Calculate column widths
    max_token = max(len(str(token)) for token, _ in symtab)
    max_type = max(len(str(type_)) for _, type_ in symtab)
    max_token = max(max_token, len("Token"))  # Ensure header fits
    max_type = max(max_type, len("Type"))

    # Define formatting strings
    border = "+" + "-" * (max_token + 2) + "+" + "-" * (max_type + 2) + "+"
    row_format = f"| {{:<{max_token}}} | {{:<{max_type}}} |"

    # Print table
    print(border)
    print(row_format.format("Token", "Type"))
    print(border)
    for token, type_ in symtab:
        print(row_format.format(str(token), str(type_)))
    print(border)

# Iterate over all files in the directory
i = 1
for filename in sorted(os.listdir(testcases_dir)): 
    if specific_filename is not None:
        if filename != specific_filename:
            continue

    filepath = os.path.join(testcases_dir, filename)
    if os.path.isfile(filepath):
        with open(filepath, 'r') as file:
            data = file.read()
        print(f"Parsing file: {filepath}")
        current_filename = filepath
        input_text = strip_file(data)

        lines = data.split('\n')
        new_file = ""
        for line in lines:
            new_file += line.strip()


        hash = SHA256.new() 
        hash.update(input_text.encode())
        input_hash = hash.hexdigest()

        root = parser.parse(data)
        print("Final Symbol Table:\n")
        print(symtab)
        print("\n")

        if input_hash not in testcase_hashes:
            testcase_hashes.append(input_hash)

            with open(f"{stress_testing}{uuid.uuid4()}.c", "w") as f:
                f.write(data)
                f.close()

            with open(f"./testcasehashes.txt", "a") as f:
                f.write(input_hash)
                f.write("\n")
                f.close()
            
            stress_test_file += 1

        if len(argv) > 1:
            if "-g" in strargv or "--graph" in strargv:
                graph = root.to_graph()
                graph.render(f'renderedTrees/{filename+""}', format='png')
                print(f"Parse tree saved as renderedTrees/{filename}.png")
                graph = symtab.to_graph()
                graph.render(f'renderedSymbolTables/{filename}', format='png', cleanup=True)
                print(f"Symbol table tree saved as renderedSymbolTables/{filename}.png")

        # parseTree_to_3AC(root,symtab)
        i += 1

        symtab.clear()

    symbol_table.clear()
    typedef_names.clear()
    lines = ""  
    lexer.lineno = 0
