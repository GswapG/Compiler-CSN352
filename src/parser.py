import ply.yacc as yacc
import os
from tokens import tokens  # Assuming you have a matching lexer
from sys import argv
from ply import yacc

from lexer import *
from tree import *
from symtab_new import *

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

    print(f"HELLO IM ADDING IDENTIFIER {p[1]} to the p[0].vars so {p[0].vars}")
    check = symtab.lookup(p[1])
    print(f"HELL NAHH DID I FIND {p[1]} IN SYMBOL TABLE? {check}")
    if(check!=None):
        p[0].dtypes = [check.type]
        print(check.type)
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
    elif len(p) == 4 and p[2] == ".":
        p[0] = Node("postfix_expression", [p[1], p[3]])
    elif len(p) == 4 and p[3] != ")":
        p[0] = Node("postfix_expression", [p[1], p[2], p[3]])
    elif len(p) == 4:
        p[0] = Node("postfix_expression", [p[1]])
        p[0].iscall = True
    elif len(p) == 5:
        print(p[2])
        if p[2] == '[':
            for i in range(0,len(p[1].vars)):
                p[1].vars[i] = '@' + p[1].vars[i]
            print(p[1].vars)
        p[0] = Node("postfix_expression", [p[1], p[3]])
        if p[2] == '(':
            p[0].iscall = True
        
        print(f"IN POSTFIX EXPRSSION IN HERE? => {p[0].return_type}")

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

        # print(f"here2 |{p[0].vars[0]}|{variable_identifier}|{variable.type}|{struct_name}")

        # print(f"here |{struct_table.name}|{struct_table.type}|{struct_table.kind}|{struct_table.node}|{struct_table.child}|")
        # print(f"here |{variable_identifier}|{struct_name}|")

        # checking if the identifier exists in the struct 
        exists = False
        for entry in struct_scope.entries:
            if entry.name == identifier:
                exists = True

        if not exists:
            print(f"The identifier '{identifier}' does not exist in the struct {struct_name}")

        p[0].vars = [f"{struct_name} {variable.name} {identifier}"]
        print(f"control f karle {p[0].vars}")

    if len(p) == 5 and p[2] == "(" and len(p[0].vars) > 0:
        print(p[0].vars)
        func_params = symtab.search_params(p[0].vars[0])
        argument_list = p[3].param_list
        print(f"argument_list => {argument_list}")
        print(f"func_params => {func_params}")
        for z in func_params:
            print(z.type)
        # if len(argument_list) != len(func_params):
        #     raise Exception("incorrect function parameter length")
        
        i = 0
        j = 0
        while i < len(argument_list) and j < len(func_params):
            if func_params[j].type == '...':
                i += 1
                pass
            else:
                print(func_params[j].type.rstrip(' '))
                print(argument_list[i].rstrip(' '))


                if func_params[j].type.rstrip(' ') != argument_list[i].rstrip(' '):
                    raise Exception("Invalid Function Paramters")
                else:
                    i+=1
                    j+=1
        print(i)
        print(j)
        if i != len(argument_list):
            raise Exception("Invalid Function Parameter Length")
        if j != len(func_params):
            if j==len(func_params) - 1 and func_params[j].type =='...':
                pass
            else:
                raise Exception("Invalid Function Parameter Length") 
            

        p[0].vars = [p[0].vars[0]]
        p[0].return_type = p[1].return_type

    if len(p) == 4 and p[2] == "(":
        func_params = symtab.search_params(p[0].vars[0])
        argument_list = []

        if len(argument_list) != len(func_params):
            raise Exception("incorrect function parameter length")

        for argument, parameter in zip(argument_list, func_params):
            if parameter.type.rstrip(" ") != symtab.lookup(argument).type.rstrip(" "):
                raise Exception(f"Error: function parameter mismatch for {parameter.type} & {argument}")
    print(f"IN POSTFIX EXPRSSION => {p[0].return_type}")

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
        print(p[0].vars)
        print(f"ahaha {p[1].return_type}")
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
    elif len(p) == 3:
        p[0] = Node("unary_expression", [p[1], p[2]])
        if p[1].children[0].type =='&':
            p[0].is_address = True
            for i in range(0,len(p[0].vars)):
                p[0].vars[i] = '!' + p[0].vars[i]
 
        if p[1].children[0].type == '*':
            for i in range(0,len(p[0].vars)):
                p[0].vars[i] = '@' + p[0].vars[i]

    elif len(p) == 5:
        p[0] = Node("unary_expression", [p[1], p[3]])
    # print("debug")
    # print(p[0].vars)

    print(f"UNARY EXPRESSION => {p[1].return_type}")

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
    # print(p[1].return_type)

# Cast expressions
def p_cast_expression(p):
    '''cast_expression : unary_expression
                      | LPAREN type_name RPAREN cast_expression'''
    if len(p) == 2:
        p[0] = Node("cast_expression", [p[1]])
        print(p[1].return_type)
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
        print(f"maa chudaale {p[1].return_type}")
    else:
        p[0] = Node("multiplicative_expression", [p[1], p[2], p[3]])
    
    dtype1 = None
    deref_count = 0
    ref_count = 0

    if len(p[1].vars) > 0:
        print(f"what is here {p[1].vars}")
        
        copy = p[1].vars[0]
        while isinstance(copy, str):
            if copy[0] == '@':
                deref_count += 1
                copy = copy[1:]
            elif copy[0] == '!':
                ref_count += 1
                copy = copy[1:]
            else:
                break

        print(f"lol {copy}")

        if isinstance(copy, str) and ' ' in copy:
            name, _, identifier = copy.split(' ')
            print(name)
            print(_)
            print(identifier)

            entry = symtab.search_struct(name, identifier)
            if entry is None:
                raise Exception(f"identifier {identifier} does not exist in the struct {name}")

            print(entry.type)
            dtype1 = entry.type

        else:
            dtype1 = symtab.lookup(copy).type

        for i in range(0, deref_count):
            if isinstance(dtype1,str) and dtype1[0] == '*':
                dtype1 = dtype1[1:]
            else:
                raise TypeError("Invalid Deref Op")  
            
        for j in range(0, ref_count):
            if isinstance(dtype1, str):
                dtype1 = "*" + dtype1

    for var in p[1].vars:
        deref_count = 0
        ref_count = 0

        while isinstance(var, str):
            if var[0] == '@':
                deref_count += 1
                var = var[1:]
            elif var[0] == '!':
                ref_count += 1
                var = var[1:]
            else:
                break

        print(f"var => {var}")

        if isinstance(var, str) and ' ' in var:
            name, _, identifier = var.split(' ')
            print(name)
            print(_)
            print(identifier)

            entry = symtab.search_struct(name, identifier)
            if entry is None:
                raise Exception(f"identifier {identifier} does not exist in the struct {name}")

            print(entry.type)
            type_ = entry.type

        else:
            type_ = symtab.lookup(var).type

        # if deref_count < ref_count:
        #     raise Exception(f"deref_count {deref_count} cannot be lower than the ref_count {ref_count}")

        for i in range (0, deref_count):
            if isinstance(type_,str) and type_[0] == '*':
                type_ = type_[1:]
            else:
                raise TypeError("Invalid Deref Op")
            
        for j in range(0, ref_count):
            if isinstance(type_, str):
                type_ = "*" + type_

        print(dtype1)
        print(type_)
            
        if type_.rstrip(' ') != dtype1.rstrip(' ') and ((isinstance(var, str) and ' ' in var) or symtab.lookup(var).kind != "function"):
            print(p[1].vars)
            raise ValueError(f"Incompatible multiplicative op with '{var}'")
        
    if len(p) == 4:
        for var in p[3].vars:
            deref_count = 0
            ref_count = 0

            while isinstance(var, str):
                if var[0] == '@':
                    deref_count += 1
                    var = var[1:]
                elif var[0] == '!':
                    ref_count += 1
                    var = var[1:]
                else:
                    break

            print(f"var => {var}")

            if isinstance(var, str) and ' ' in var:
                name, _, identifier = var.split(' ')
                print(name)
                print(_)
                print(identifier)

                entry = symtab.search_struct(name, identifier)
                print(entry.type)
                type_ = entry.type

            else:
                type_ = symtab.lookup(var).type

            # if deref_count < ref_count:
            #     raise Exception(f"deref_count {deref_count} cannot be lower than the ref_count {ref_count}")

            for i in range (0, deref_count):
                if isinstance(type_,str) and type_[0] == '*':
                    type_ = type_[1:]
                else:
                    raise TypeError("Invalid Deref Op")
                
            for j in range(0, ref_count):
                if isinstance(type_, str):
                    type_ = "*" + type_

            if type_.rstrip(' ') != dtype1.rstrip(' ') and ((isinstance(var, str) and ' ' in var) or symtab.lookup(var).kind != "function"):
                raise ValueError(f"Incompatible multiplicative op with '{var}'")
            
    # if here then no exception thrown
    print(f"multiplicative_Expression => {p[1].return_type}")
    p[0].return_type = p[1].return_type

def p_additive_expression(p):
    '''additive_expression : multiplicative_expression
                          | additive_expression PLUS multiplicative_expression
                          | additive_expression MINUS multiplicative_expression'''
    if len(p) == 2:
        p[0] = Node("additive_expression", [p[1]])
    else:
        p[0] = Node("additive_expression", [p[1], p[2], p[3]])
    
    dtype1 = None
    deref_count = 0
    ref_count = 0

    if len(p[1].vars) > 0:
        print(f"what is here {p[1].vars}")
        
        copy = p[1].vars[0]
        while isinstance(copy, str):
            if copy[0] == '@':
                deref_count += 1
                copy = copy[1:]
            elif copy[0] == '!':
                ref_count += 1
                copy = copy[1:]
            else:
                break

        print(f"lol {copy}")

        if isinstance(copy, str) and ' ' in copy:
            name, _, identifier = copy.split(' ')
            print(name)
            print(_)
            print(identifier)

            entry = symtab.search_struct(name, identifier)
            if entry is None:
                raise Exception(f"identifier {identifier} does not exist in the struct {name}")

            print(entry.type)
            dtype1 = entry.type

        else:
            dtype1 = symtab.lookup(copy).type

        for i in range(0, deref_count):
            if isinstance(dtype1,str) and dtype1[0] == '*':
                dtype1 = dtype1[1:]
            else:
                raise TypeError("Invalid Deref Op")  
            
        for j in range(0, ref_count):
            if isinstance(dtype1, str):
                dtype1 = "*" + dtype1

    for var in p[1].vars:
        deref_count = 0
        ref_count = 0

        while isinstance(var, str):
            if var[0] == '@':
                deref_count += 1
                var = var[1:]
            elif var[0] == '!':
                ref_count += 1
                var = var[1:]
            else:
                break

        print(f"var => {var}")

        if isinstance(var, str) and ' ' in var:
            name, _, identifier = var.split(' ')
            print(name)
            print(_)
            print(identifier)

            entry = symtab.search_struct(name, identifier)
            if entry is None:
                raise Exception(f"identifier {identifier} does not exist in the struct {name}")

            print(entry.type)
            type_ = entry.type

        else:
            type_ = symtab.lookup(var).type

        # if deref_count < ref_count:
        #     raise Exception(f"deref_count {deref_count} cannot be lower than the ref_count {ref_count}")

        for i in range (0, deref_count):
            if isinstance(type_,str) and type_[0] == '*':
                type_ = type_[1:]
            else:
                raise TypeError("Invalid Deref Op")
            
        for j in range(0, ref_count):
            if isinstance(type_, str):
                type_ = "*" + type_
            
        if type_.rstrip(' ') != dtype1.rstrip(' ') and ((isinstance(var, str) and ' ' in var) or symtab.lookup(var).kind != "function"):
            print(p[1].vars)
            raise ValueError(f"Incompatible addition op with '{var}'")
        
    if len(p) == 4:
        for var in p[3].vars:
            deref_count = 0
            ref_count = 0

            while isinstance(var, str):
                if var[0] == '@':
                    deref_count += 1
                    var = var[1:]
                elif var[0] == '!':
                    ref_count += 1
                    var = var[1:]
                else:
                    break

            print(f"var => {var}")

            if isinstance(var, str) and ' ' in var:
                name, _, identifier = var.split(' ')
                print(name)
                print(_)
                print(identifier)

                entry = symtab.search_struct(name, identifier)
                print(entry.type)
                type_ = entry.type

            else:
                type_ = symtab.lookup(var).type

            # if deref_count < ref_count:
            #     raise Exception(f"deref_count {deref_count} cannot be lower than the ref_count {ref_count}")

            for i in range (0, deref_count):
                if isinstance(type_,str) and type_[0] == '*':
                    type_ = type_[1:]
                else:
                    raise TypeError("Invalid Deref Op")
                
            for j in range(0, ref_count):
                if isinstance(type_, str):
                    type_ = "*" + type_

            if type_.rstrip(' ') != dtype1.rstrip(' ') and ((isinstance(var, str) and ' ' in var) or symtab.lookup(var).kind != "function"):
                raise ValueError(f"Incompatible addition op with '{var}'")
            
    # if here then no exception thrown

    p[0].return_type = p[1].return_type
    
def p_shift_expression(p):
    '''shift_expression : additive_expression
                       | shift_expression LEFT_OP additive_expression
                       | shift_expression RIGHT_OP additive_expression'''
    if len(p) == 2:
        p[0] = Node("shift_expression", [p[1]])
        print(p[1].return_type)
    else:
        p[0] = Node("shift_expression", [p[1], p[2], p[3]])

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
        for var in p[1].vars:
            while isinstance(var,str) and var[0] == '@':
                var = var[1:]
            if symtab.lookup(var) == None:
                raise ValueError(f"No symbol '{var}' in the symbol table")
        for var in p[1].vars:
            c1 = 0
            while isinstance(var,str) and var[0] == '@':
                var = var[1:]
                c1 +=1
            type1 = symtab.lookup(var).type
            for i in range(0,c1):
                if type1[0]=='*':
                    type1 = type1[1:]
                else:
                    raise TypeError("Invalid Deref in Conditional")
            for var2 in p[3].vars:
                c2 = 0
                while isinstance(var2,str) and var2[0] == '@':
                    var2 = var2[1:]
                    c2+=1
                
                type2 = symtab.lookup(var2).type
                for i in range(0,c2):
                    if type2[0]=='*':
                        type2 = type2[1:]
                    else:
                        raise TypeError("Invalid Deref in Conditional")
                if type1.rstrip(' ') != type2.rstrip(' '):
                    print(type1,type2)
                    raise ValueError(f"Incompatible relational op with '{var}' and '{var2}'")
                
    print(p[1].return_type)

def p_equality_expression(p):
    '''equality_expression : relational_expression
                          | equality_expression EQ_OP relational_expression
                          | equality_expression NE_OP relational_expression'''
    if len(p) == 2:
        p[0] = Node("equality_expression", [p[1]])
        print(p[1].return_type)
    else:
        p[0] = Node("equality_expression", [p[1], p[2], p[3]])
        for var in p[1].vars:
            if symtab.lookup(var) == None:
                raise ValueError(f"No symbol '{var}' in the symbol table")

def p_and_expression(p):
    '''and_expression : equality_expression
                     | and_expression AND equality_expression'''
    if len(p) == 2:
        p[0] = Node("and_expression", [p[1]])
        print(p[1].return_type)
    else:
        p[0] = Node("and_expression", [p[1], p[2], p[3]])

def p_exclusive_or_expression(p):
    '''exclusive_or_expression : and_expression
                              | exclusive_or_expression XOR and_expression'''
    if len(p) == 2:
        p[0] = Node("exclusive_or_expression", [p[1]])
        print(p[1].return_type)
    else:
        p[0] = Node("exclusive_or_expression", [p[1], p[2], p[3]])

def p_inclusive_or_expression(p):
    '''inclusive_or_expression : exclusive_or_expression
                              | inclusive_or_expression OR exclusive_or_expression'''
    if len(p) == 2:
        p[0] = Node("inclusive_or_expression", [p[1]])
        print(p[1].return_type)
    else:
        p[0] = Node("inclusive_or_expression", [p[1], p[2], p[3]])

def p_logical_and_expression(p):
    '''logical_and_expression : inclusive_or_expression
                             | logical_and_expression AND_OP inclusive_or_expression'''
    if len(p) == 2:
        p[0] = Node("logical_and_expression", [p[1]])
        print(p[1].return_type)
    else:
        p[0] = Node("logical_and_expression", [p[1], p[2], p[3]])

def p_logical_or_expression(p):
    '''logical_or_expression : logical_and_expression
                            | logical_or_expression OR_OP logical_and_expression'''
    if len(p) == 2:
        p[0] = Node("logical_or_expression", [p[1]])
        print(p[1].return_type)
    else:
        p[0] = Node("logical_or_expression", [p[1], p[2], p[3]])

def p_conditional_expression(p):
    '''conditional_expression : logical_or_expression
                             | logical_or_expression QUESTION expression COLON conditional_expression'''
    if len(p) == 2:
        p[0] = Node("conditional_expression", [p[1]])
        print(p[1].return_type)
    else:
        p[0] = Node("conditional_expression", [p[1], p[3], p[5]])

def p_assignment_expression(p):
    '''assignment_expression : conditional_expression
                            | unary_expression assignment_operator assignment_expression'''
    if len(p) == 2:  # Case: conditional_expression
        p[0] = Node("assignment_expression", [p[1]])
        print(f"assignment expresion => {p[0].vars}")
        print(p[1].return_type)
        print(p[0].return_type)
    else:  # Case: unary_expression assignment_operator assignment_expression
        p[0] = Node("assignment_expression", [p[1], p[2], p[3]])

        # print(p[0].vars)
        # if len(p[0].vars) != 1:
        #     raise Exception("left this error comment for future debugging purpose. wrote this for checking for statements A = B; if A already exists in symbol table and for that when i look for A in the unary_expression i expect its length to be 1. if it's not 1 then this error is thrown and you are suppose to fix this goodluck")

        print(f"ok im here => {p[0].vars}")

        for var in p[0].vars:
            new_var = []
            if isinstance(var, str) and ' ' in var:
                new_var = var.split(' ')[1: -1]
            else:
                new_var.append(var)

            for var in new_var:    
                while isinstance(var, str):
                    if var[0] == '@':
                        var = var[1:]
                    elif var[0] == '!':
                        var = var[1:]
                    else:
                        break
                if symtab.lookup(var) == None:
                    raise ValueError(f"No symbol '{var}' in the symbol table")
                
        deref_count = 0
        ref_count = 0
        if isinstance(p[0].vars[0], str) and ' ' in p[0].vars[0]:
            vars = p[0].vars[0].split(' ')
            struct_name = vars[0]
            struct_table = symtab.lookup(struct_name)
            struct_scope = struct_table.child 

            lhs = None
            for entry in struct_scope.entries:
                if entry.name == vars[-1]:
                    lhs = entry 
                    break

        else:
            var = p[0].vars[0]
            while isinstance(var, str):
                if var[0] == '@':
                    var = var[1:]
                    deref_count += 1
                elif var[0] == '!':
                    var = var[1:]
                    ref_count += 1
                else:
                    break

                ## can support references here?
            lhs = symtab.lookup(var)

        if lhs is None:
            raise Exception(f"identifier {p[0].vars[0]} does not exist")
        
        lhs_no_const = (lhs.type if "const " not in lhs.type else ''.join(_ for _ in lhs.type.split("const ")))
        print(lhs_no_const)
        print(deref_count)

        for i in range(0, deref_count):
            if lhs_no_const[0] == '*':
                lhs_no_const = lhs_no_const[1:]
            else:
                raise TypeError("invalid deref during assignment")
        
        for j in range(0, ref_count):
            lhs_no_const = "*" + lhs_no_const
        
        if lhs.type.startswith("const "):
            raise TypeError(f"Cannot re-assign value to const variable '{lhs.name}' of type '{lhs.type}'")

        if lhs.kind != 'variable' and lhs.kind != 'parameter':
            raise TypeError(f"Value can only be assigned to variable/param types!")

        for rhs_var in p[3].vars:
            deref_count = 0
            ref_count = 0

            if isinstance(rhs_var, str) and ' ' in rhs_var:
                name, _, identifier = rhs_var.split(' ')
                print(name)
                print(_)
                print(identifier)

                entry = symtab.search_struct(name, identifier)
                if entry is None:
                    raise Exception(f"identifier {identifier} does not exist in the struct {name}")

                print(entry.type)
                rhs_decl = entry

            else:
                while isinstance(rhs_var, str):
                    if rhs_var[0] == '@':
                        rhs_var = rhs_var[1:]
                        deref_count += 1

                    elif rhs_var[0] == '!':
                        rhs_var = rhs_var[1:]
                        ref_count += 1

                    else:
                        break
                rhs_decl = symtab.lookup(rhs_var)

            print("NIGGGAAAAAA")
            print(rhs_var)
            print(rhs_decl.type)
            og_type = rhs_decl.type
            
            # if p[0].is_address:
            #     rhs_decl.type = '*' + rhs_decl.type

            for i in range(0, deref_count):
                if isinstance(rhs_decl.type,str) and rhs_decl.type[0] == '*':
                    rhs_decl.type = rhs_decl.type[1:]
                else:
                    raise TypeError("Invalid Deref Op")  
                
            for j in range(0, ref_count):
                if isinstance(rhs_decl.type, str):
                    rhs_decl.type = "*" + rhs_decl.type

            if rhs_decl.type.startswith("const "):
                rhs_decl.type = rhs_decl.type[6:]
            
            if rhs_decl.type != lhs_no_const:
                # rhs_decl.type = og_type
                raise ValueError(f"Type mismatch in assignment of {lhs.name} and {rhs_decl.name}\n {lhs_no_const} {rhs_decl.type}")
        
        rhs_decl.type = og_type
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

def p_expression(p):
    '''expression : assignment_expression
                 | expression COMMA assignment_expression'''
    if len(p) == 2:
        p[0] = Node("expression", [p[1]])
    else:
        p[0] = Node("expression", [p[1], p[3]])
    
    # print(f"myboii {p[0].return_type}")

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
    if(len(datatypeslhs)>0 and datatypeslhs[0]=="typedef"):
        for var in p[0].vars:
            typedef_names.add(str(var))
            print(f"hereganggang |{var}|")
    datatypeslhs=[]

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
    datatypeslhs=p[0].dtypes
    print(f"declaration_specifiers => {p[0].dtypes}")

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

    tokens = data_type.strip().split()
    
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
    for dtype in datatypeslhs:
        base_type += dtype
        base_type += " "
        abcd += 1
    base_type = base_type[:-1]

    # validate_c_datatype(base_type)

    print(f"ok here => {p[0].vars}")
    print(base_type)
    print(p[0].vars)

    for decl in p[0].vars:
        kind2="variable"
        print(f"find me here |{decl}|{base_type}|{kind2}|{abcd}")
        if(base_type.split(" ")[0]=="typedef" and len(base_type.split(" "))>=1):
            name = base_type.split(" ")[-1]
            kind2=f"{name}"
            base_type=f"{name}"
        print(base_type)
        if isinstance(decl,str) and decl[0] == '%' :
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
        else:
            var_sym = SymbolEntry(
                name=str(decl),
                type=str(base_type),
                kind=str(kind2)
            )
            symtab.add_symbol(var_sym)
    
    print(p[0].rhs)
    for var in p[0].rhs:
        if isinstance(var, str) and ' ' in var:
            name, _, identifier = var.split(' ')
            if symtab.search_struct(name, identifier) == None:
                raise ValueError(f"No symbol '{var}' in the symbol table")

            continue
        while isinstance(var, str):
            if var[0] == '@':
                var = var[1:]
            elif var[0] == '!':
                var = var[1:]
            else:
                break
        if symtab.lookup(var) == None:
            raise ValueError(f"No symbol '{var}' in the symbol table")
        
    var = p[0].vars[0]
    deref_count = 0
    ref_count = 0

    print(var)
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

    print(var)

    base_no_const = symtab.lookup(var).type
    if "const " in base_no_const:
        base_no_const = ' '.join(word for word in base_no_const.split() if word != "const")
    if "static " in base_no_const:
        base_no_const = ' '.join(word for word in base_no_const.split() if word != "static")
    checkfunc = True
    if len(p) == 4:
        checkfunc = not p[3].iscall

    
    ## struct or union
    if (symtab.lookup(base_no_const) is not None and (symtab.lookup(base_no_const).type == 'struct' or symtab.lookup(base_no_const).type == 'union')) or ('struct' in base_no_const or 'union' in base_no_const) and not base_no_const.startswith("*"):
        print("ahahahah")
        print(p[0].rhs)
        print(p[0].isbraces)
        print(p[0].is_address)

        if p[0].isbraces:
            struct_name = base_no_const.split(' ')[-1]
            struct_scope = symtab.lookup(struct_name).child
            struct_entries = struct_scope.entries

            if len(struct_entries) < len(p[0].rhs):
                raise Exception("Number of identifiers in struct doesnt match with initialiser list length")

            for struct_entry, list_entry in zip(struct_entries, p[0].rhs):
                deref_count = 0
                ref_count = 0
                while isinstance(list_entry, str):
                    if list_entry[0] == '@':
                        deref_count += 1
                        list_entry = list_entry[1:]
                    elif list_entry[0] == '!':
                        ref_count += 1
                        list_entry = list_entry[1:]
                    else:
                        break

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
                    deref_count = 0
                    ref_count = 0

                    rhs_var = p[0].rhs[0]
                    while isinstance(rhs_var, str):
                        if rhs_var[0] == '@':
                            deref_count += 1
                            rhs_var = rhs_var[1:]
                        elif rhs_var[0] == '!':
                            ref_count += 1
                            rhs_var = rhs_var[1:]
                        else:
                            break

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
        print(f"wtf {p[0].rhs}")
        for rhs_var in p[0].rhs:
            deref_count = 0
            ref_count = 0
            while isinstance(rhs_var, str):
                if rhs_var[0] == '@':
                    deref_count += 1
                    rhs_var = rhs_var[1:]
                elif rhs_var[0] == '!':
                    ref_count += 1
                    rhs_var = rhs_var[1:]
                else:
                    break
            
            if isinstance(rhs_var, str) and ' ' in rhs_var:
                name, _, identifier = rhs_var.split(' ')
                rhs = symtab.search_struct(name, identifier)
            else: 
                rhs = symtab.lookup(rhs_var)

            original_type = rhs.type

            # if p[0].is_address:
            #     rhs.type = '*' + rhs.type

            print(rhs.type)
            print(original_type)

            for i in range(0, deref_count):
                if isinstance(rhs.type,str) and rhs.type[0] == '*':
                    rhs.type = rhs.type[1:]
                else:
                    raise TypeError("Invalid Deref Op")  
                
            for j in range(0, ref_count):
                if isinstance(rhs.type, str):
                    rhs.type = "*" + rhs.type

            print(rhs.type)
            print(original_type)

            array_check = base_no_const.rstrip(' ').lstrip('*')

            if p[0].isbraces:
                if symtab.lookup(rhs_var) is not None and array_check != (symtab.lookup(rhs_var)).type.rstrip(' '):
                    raise TypeError(f"Type mismatch in declaration of {p[0].vars[0]} because of {rhs_var}\n| base_type = {base_no_const} |\n| rhs_type = {(symtab.lookup(rhs_var)).type} |")
                # if checkfunc and symtab.lookup(rhs_var) is not None and symtab.lookup(rhs_var).kind == 'function':
                #     raise Exception("Can't assign value of function")
            else:

                if (base_no_const.rstrip(' ') != rhs.type.rstrip(' ') and not (base_no_const.split(" ")[0]=="enum" and rhs.type=="int")):
                    raise TypeError(f"Type mismatch in declaration of {p[0].vars[0]} because of {rhs_var}\n| base_type = {base_no_const} |\n| rhs_type = {rhs.type} |")

                print("niche waali if statement kisne likhi hai ye bc")

                # if checkfunc and symtab.lookup(rhs_var) is not None and symtab.lookup(rhs_var).kind == 'function':
                #     raise Exception("Can't assign value of function")

                
            rhs.type = original_type
            
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
        # p[0].dtypes.append(str(p[1].children[0])+" "+p[2])
        symbol_table.append((p[2], str(p[1].children[0])))
        
        struct_name = p[2]
        sym_scope_level = symtab.current_scope_level - 1
        struct_sym = SymbolEntry(
            name=str(struct_name),
            type=f"{p[0].dtypes[0]}",
            kind=f"{p[0].dtypes[0]}"
        )

        # for entry in symtab.scopes[-1]:
        #     if symtab.scopes[-1][entry].scope_name == f"block@{symtab.current_scope_level}":
        #         symtab.scopes[-1][entry].scope_name = str(p[1].children[0]) + " " + struct_name
        
        symtab.add_symbol(struct_sym)
        # symtab.current_scope_level -= 1

    else:
        p[0] = Node("struct_or_union_specifier", [p[1], p[2]])
        p[0].dtypes.append(p[2])

    

# def p_struct_or_union_specifier_error(p):
#     '''struct_or_union_specifier : struct_or_union LBRACE struct_declaration_list error
#                                 | struct_or_union IDENTIFIER LBRACE struct_declaration_list error'''

#     print("Error: Missing '}' Brace")


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
        p[0].vars[0] = '#'*p[0].is_const + p[0].vars[0] + '$'*p[0].pointer_count
        p[0].pointer_count = 0
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
        print("burr",base_type)
        # validate_c_datatype(base_type)

    if len(p) > 2 and p[2] == '(':
        print("lesgo",p[1].fdtypes)
        func_name = p[1].vars[0] #check gang
        base_type = ''
        for dtype in p[1].fdtypes:
            base_type += dtype
            base_type += " "
        
        base_type=base_type[:-1]
        print(f"base_type123 = {base_type}")
        # Add function to GLOBAL scope
        func_sym = SymbolEntry(
            name=str(func_name),
            type=str(base_type),  # Return type from declaration_specifiers
            kind="function"
        )
        symtab.add_symbol(func_sym)
        symtab.to_add_parent = True
        symtab.the_parent = symtab.lookup(func_name) 

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

    p[0].pointer_count += 1

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

        symtab.add_symbol(param_sym)


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
        print(f"initializer_list => {p[0].vars}")
        print(f"initializer_list => {p[0].rhs}")
    elif len(p) == 4:
        p[0] = Node("initializer_list", [p[1], p[3]])
        print(f"initializer_list => {p[0].vars}")
        print(f"initializer_list => {p[0].rhs}")
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
        # p[0].enter_scope = p[2]  # Store scope actions in AST node
        # p[0].exit_scope = p[4]

    # -- Scope Handling --
    # if len(p) == 3:  # Empty block
    #     symtab.enter_scope()
    #     symtab.exit_scope()
    # else:
    #     # Mid-rule actions for scope management
    #     def enter_scope(p):
    #         symtab.enter_scope()
    #     p[0].scope_enter = enter_scope
    #     p[0].scope_exit = symtab.exit_scope

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

# def p_iteration_statement_error_1(p):
#     '''iteration_statement : WHILE LPAREN expression error statement
#                           | DO statement WHILE LPAREN expression error SEMICOLON
#                           | FOR LPAREN expression_statement expression_statement error statement
#                           | FOR LPAREN expression_statement expression_statement expression error statement
#                           | FOR LPAREN declaration expression_statement error statement
#                           | FOR LPAREN declaration expression_statement expression error statement'''
    
#     print("Error: Missing ')' Paranthesis")

# def p_iteration_statement_error_2(p):
#     '''iteration_statement : DO statement WHILE LPAREN expression RPAREN error'''

#     print("Error: Missing Semicolon")

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
    print(f"base_type = {base_type}")
    
    # func_sym = SymbolEntry(
    #     name=str(func_name),
    #     type=str(base_type),  # Return type from declaration_specifiers
    #     kind="function"
    # )

    global returns
    while len(func_name) > 0 and func_name[-1] == '$':
        func_name = func_name[:-1]
    b_type = symtab.lookup(func_name).type

    if len(returns) > 1:
        raise Exception("Multiple Return Types")

    for type in returns:
        print(b_type)
        if b_type.rstrip(' ') != type.rstrip(' '):
            print(b_type)
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
    
# Build parser
parser = yacc.yacc(debug=True)
testcases_dir = './tests/testing'

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
    filepath = os.path.join(testcases_dir, filename)
    if os.path.isfile(filepath):
        with open(filepath, 'r') as file:
            data = file.read()
        print(f"Parsing file: {filepath}")
        current_filename = filepath
        input_text = data
        lines = data.split('\n')

        root = parser.parse(data)
        #root.dfs2()
        # print_symbol_table(symbol_table)
        print("Final Symbol Table:\n")
        print(symtab)
        print("\n")

        if len(argv) > 1 and (str(argv[1]) == "-g" or str(argv[1]) == "--graph"):
            graph = root.to_graph()
            graph.render(f'renderedTrees/{filename+""}', format='png')
            print(f"Parse tree saved as renderedTrees/{filename}.png")
            graph = symtab.to_graph()
            graph.render(f'renderedSymbolTables/{filename}', format='png', cleanup=True)
            print(f"Symbol table tree saved as renderedSymbolTables/{filename}.png")

        i += 1

        # symtab.clear()

        # if i>=2 : break
    symbol_table.clear()
    typedef_names.clear()
    lines = ""  
    lexer.lineno = 0
