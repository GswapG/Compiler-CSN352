# -*- coding: utf-8 -*-
import ply.yacc as yacc
import os
from lexer import *
from collections import deque
from tokens import tokens  # Assuming you have a matching lexer
from graphviz import Digraph
# AST

class Node:
    def __init__(self, type, children = None):
        self.type = type
        self.children = []
        if children:
            self.children = children
    def __repr__(self):
        return f"Node({self.type})"

    def to_graph(self, graph=None):
        if graph is None:
            graph = Digraph()
            graph.node(str(id(self)), label=self.type)
        
        for child in self.children:
            if isinstance(child, Node):
                graph.node(str(id(child)), label=child.type)
                graph.edge(str(id(self)), str(id(child)))
                child.to_graph(graph)
            else:
                child_id = f"{id(self)}_{id(child)}"
                graph.node(child_id, label=str(child))
                graph.edge(str(id(self)), child_id)
        
        return graph
    
def dfs(node, indent=0):
    """Recursively prints the AST."""
    # Check if the node is a string or a Node object
    if isinstance(node, Node):
        # Print the current node's type
        print(" " * indent + f"Node: {node.type}")
        
        # Recursively print each child
        for child in node.children:
            dfs(child, indent + 4)
    else:
        print(" " * indent + f"Value: {node}")
      
def level_order(node):
    queue = deque()
    queue.append(node)
    while(queue):
        sz = len(queue)
        for i in range(0,sz):
            v = queue.popleft()
            if isinstance(v,Node):
                print(f"Node: {v.type}",end=" ")
                for u in v.children:
                    queue.append(u)
            else:
                print(f"Value: {v}",end = " ")
        print("\n \n")
    
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
    '''primary_expression : IDENTIFIER
                          | constant
                          | string
                          | LPAREN expression RPAREN
                          | generic_selection'''
    if len(p) == 2:
        p[0] = Node("primary_expression", [p[1]])
    elif len(p) == 4:
        p[0] = Node("primary_expression", [p[2]])

def p_constant(p):
    '''constant : CONSTANT
                | CHAR_CONSTANT
                | enumeration_constant'''
    p[0] = Node("constant", [p[1]])  # Include the constant value

def p_enumeration_constant(p):
    '''enumeration_constant : IDENTIFIER'''
    p[0] = Node("enumeration_constant", [p[1]])

def p_string(p):
    '''string : STRING_LITERAL'''
    p[0] = Node("string", [p[1]])

def p_generic_selection(p):
    '''generic_selection : GENERIC LPAREN assignment_expression COMMA generic_assoc_list RPAREN '''
    p[0] = Node("generic_selection", [p[3], p[5]])

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
    elif len(p) == 4 and p[3]!=")":
        p[0] = Node("postfix_expression", [p[1], p[2], p[3]])
    elif len(p) == 4:
        p[0] = Node("postfix_expression", [p[1]])
    elif len(p) == 5:
        p[0] = Node("postfix_expression", [p[1], p[3]])
    elif len(p) == 7:
        p[0] = Node("postfix_expression", [p[2], p[5]])
    elif len(p) == 8:
        p[0] = Node("postfix_expression", [p[2], p[5]])

def p_argument_expression_list(p):
    '''argument_expression_list : assignment_expression
                               | argument_expression_list COMMA assignment_expression'''
    if len(p) == 2:
        p[0] = Node("argument_expression_list", [p[1]])
    else:
        p[0] = Node("argument_expression_list", [p[1], p[3]])

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
    elif len(p) == 4:
        p[0] = Node("unary_expression", [p[1], p[3]])

def p_unary_operator(p):
    '''unary_operator : AND
                     | TIMES
                     | PLUS
                     | MINUS
                     | TILDE
                     | NOT '''
    p[0] = Node("unary_operator", [p[1]])

# Cast expressions
def p_cast_expression(p):
    '''cast_expression : unary_expression
                      | LPAREN type_name RPAREN cast_expression'''
    if len(p) == 2:
        p[0] = Node("cast_expression", [p[1]])
    else:
        p[0] = Node("cast_expression", [p[2], p[3]])

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

def p_additive_expression(p):
    '''additive_expression : multiplicative_expression
                          | additive_expression PLUS multiplicative_expression
                          | additive_expression MINUS multiplicative_expression'''
    if len(p) == 2:
        p[0] = Node("additive_expression", [p[1]])
    else:
        p[0] = Node("additive_expression", [p[1], p[2], p[3]])

def p_shift_expression(p):
    '''shift_expression : additive_expression
                       | shift_expression LEFT_OP additive_expression
                       | shift_expression RIGHT_OP additive_expression'''
    if len(p) == 2:
        p[0] = Node("shift_expression", [p[1]])
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

def p_equality_expression(p):
    '''equality_expression : relational_expression
                          | equality_expression EQ_OP relational_expression
                          | equality_expression NE_OP relational_expression'''
    if len(p) == 2:
        p[0] = Node("equality_expression", [p[1]])
    else:
        p[0] = Node("equality_expression", [p[1], p[2], p[3]])

def p_and_expression(p):
    '''and_expression : equality_expression
                     | and_expression AND equality_expression'''
    if len(p) == 2:
        p[0] = Node("and_expression", [p[1]])
    else:
        p[0] = Node("and_expression", [p[1], p[2], p[3]])

def p_exclusive_or_expression(p):
    '''exclusive_or_expression : and_expression
                              | exclusive_or_expression XOR and_expression'''
    if len(p) == 2:
        p[0] = Node("exclusive_or_expression", [p[1]])
    else:
        p[0] = Node("exclusive_or_expression", [p[1], p[2], p[3]])

def p_inclusive_or_expression(p):
    '''inclusive_or_expression : exclusive_or_expression
                              | inclusive_or_expression OR exclusive_or_expression'''
    if len(p) == 2:
        p[0] = Node("inclusive_or_expression", [p[1]])
    else:
        p[0] = Node("inclusive_or_expression", [p[1], p[2], p[3]])

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
    if len(p) == 2:  # Case: conditional_expression
        p[0] = Node("assignment_expression", [p[1]])
    else:  # Case: unary_expression assignment_operator assignment_expression
        p[0] = Node("assignment_expression", [p[1], p[2], p[3]])

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

def p_constant_expression(p):
    '''constant_expression : conditional_expression'''
    p[0] = Node("constant_expression", [p[1]])

# Declarations
def p_declaration(p):
    '''declaration : declaration_specifiers SEMICOLON
                  | declaration_specifiers init_declarator_list SEMICOLON
                  | static_assert_declaration'''
    # p[0] = Node("declaration", [p[1], p[2]])
    if len(p) == 4:
        p[0] = Node("declaration",[p[1],p[2]])
    else :
        p[0] = Node("declaration",[p[1]]) #fixed

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

def p_storage_class_specifier(p):
    '''storage_class_specifier : TYPEDEF
	                            | EXTERN
	                            | STATIC
	                            | THREAD_LOCAL
	                            | AUTO
	                            | REGISTER'''
    p[0] = Node("storage_class_specifier", [p[1]])

def p_init_declarator_list(p):
    '''init_declarator_list : init_declarator
                           | init_declarator_list COMMA init_declarator'''
    p[0] = Node("init_declarator_list", [p[1], p[3]] if len(p) == 4 else [p[1]])

def p_init_declarator(p):
    '''init_declarator : declarator ASSIGN initializer
                       | declarator'''
    if len(p) == 4: 
        p[0] = Node("init_declarator", [p[1], p[3]])  
    else:  # Case: declarator
        p[0] = Node("init_declarator", [p[1]])

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
                     | enum_specifier'''
    p[0] = Node("type_specifier", [p[1]])
    pass

# Structures and Unions
def p_struct_or_union_specifier(p):
    '''struct_or_union_specifier : struct_or_union LBRACE struct_declaration_list RBRACE
                                | struct_or_union IDENTIFIER LBRACE struct_declaration_list RBRACE
                                | struct_or_union IDENTIFIER'''
    if len(p) == 5:
        p[0] = Node("struct_or_union_specifier", [p[1], p[3]])
    elif len(p) == 6:
        p[0] = Node("struct_or_union_specifier", [p[1], p[2], p[4]])
    else:
        p[0] = Node("struct_or_union_specifier", [p[1], p[2]])
    pass

def p_struct_or_union(p):
    '''struct_or_union : STRUCT
                      | UNION'''
    p[0] = Node("struct_or_union", [p[1]])
    pass

def p_struct_declaration_list(p):
    '''struct_declaration_list : struct_declaration
                              | struct_declaration_list struct_declaration'''
    if len(p) == 2:
        p[0] = Node("struct_declaration_list", [p[1]])
    else:
        p[0] = Node("struct_declaration_list", [p[1], p[2]])
    pass

def p_struct_declaration(p):
    '''struct_declaration : specifier_qualifier_list SEMICOLON
                         | specifier_qualifier_list struct_declarator_list SEMICOLON
                         | static_assert_declaration'''
    if len(p) == 4:
        p[0] = Node("struct_declaration", [p[1], p[2]])
    else:
        p[0] = Node("struct_declaration", [p[1]])
    pass

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
        p[0] = Node("enum_specifier", [p[1], p[2]])
    elif len(p) == 6 and p[1] == '{':
        p[0] = Node("enum_specifier", [p[1], p[3]])
    else:
        p[0] = Node("enum_specifier", [p[1], p[2], p[4]])
    pass

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
    if len(p) == 3:
        p[0] = Node("enumerator", [p[1], p[3]])
    else:
        p[0] = Node("enumerator", [p[1]])
    pass

# Atomic types
def p_atomic_type_specifier(p):
    '''atomic_type_specifier : ATOMIC LPAREN type_name RPAREN '''
    p[0] = Node("atomic_type_specifier", [p[2]])
    pass

# Type qualifiers
def p_type_qualifier(p):
    '''type_qualifier : CONST
                     | RESTRICT
                     | VOLATILE
                     | ATOMIC'''
    p[0] = Node("type_qualifier", [p[1]])
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

# Declarators
def p_declarator(p):
    '''declarator : pointer direct_declarator
                 | direct_declarator'''
    if len(p) == 3:
        p[0] = Node("declarator", [p[1], p[2]])
    else:
        p[0] = Node("declarator", [p[1]])
    

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
                        | direct_declarator LPAREN identifier_list RPAREN '''
    
    # IDENTIFIER case
    if len(p) == 2:
        p[0] = Node("direct_declarator", [p[1]])
    
    # LPAREN declarator RPAREN case
    elif len(p) == 4 and p[1] == '(':
        p[0] = Node("direct_declarator", [p[2]])
    
    # direct_declarator LBRACKET RBRACKET case
    elif len(p) == 4 and p[2] == '[':
        p[0] = Node("array_declarator", [p[1]])
    
    # direct_declarator LBRACKET TIMES RBRACKET case
    elif len(p) == 5 and p[2] == '[' and p[3] == '*':
        p[0] = Node("vla_declarator", [p[1]])
    
    # direct_declarator LBRACKET assignment_expression RBRACKET case
    elif len(p) == 5 and p[2] == '[' and p[3] != '*':
        p[0] = Node("array_declarator", [p[1], p[3]])
    
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

# Pointers
def p_pointer(p):
    '''pointer : TIMES type_qualifier_list pointer
              | TIMES type_qualifier_list
              | TIMES pointer
              | TIMES '''
    if len(p) == 2:
        p[0] = Node("pointer", [p[1]])
    else:
        p[0] = Node("pointer", [p[1], p[2]])
    pass

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
    if len(p) == 2:
        p[0] = Node("parameter_declaration", [p[1]])
    elif len(p) == 3:
        p[0] = Node("parameter_declaration", [p[1], p[2]])
    pass

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


# Initialization
def p_initializer(p):
    '''initializer : LBRACE initializer_list RBRACE
                   | LBRACE initializer_list COMMA RBRACE
                   | assignment_expression'''
    if len(p) == 4 or len(p) == 5:  
        p[0] = Node("initializer", [p[2]])  
    else:  
        p[0] = Node("initializer", [p[1]])  


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
    '''static_assert_declaration : STATIC_ASSERT LPAREN constant_expression COMMA STRING_LITERAL RPAREN SEMICOLON '''
    p[0] = Node("static_assert_declaration", [p[3], p[5]])


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
                         | LBRACE block_item_list RBRACE '''
    if len(p) == 3:
        p[0] = Node("compound_statement", [])
    else:
        p[0] = Node("compound_statement", [p[2]])


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


def p_selection_statement(p):
    '''selection_statement : IF LPAREN expression RPAREN statement ELSE statement
                          | IF LPAREN expression RPAREN statement
                          | SWITCH LPAREN expression RPAREN statement'''
    if len(p) == 8:
        p[0] = Node("selection_statement", [p[1], p[3], p[5], p[6], p[7]])
    elif len(p) == 6:
        p[0] = Node("selection_statement", [p[1], p[3], p[5]])


def p_iteration_statement(p):
    '''iteration_statement : WHILE LPAREN expression RPAREN statement
                          | DO statement WHILE LPAREN expression RPAREN SEMICOLON
                          | FOR LPAREN expression_statement expression_statement RPAREN statement
                          | FOR LPAREN expression_statement expression_statement expression RPAREN statement
                          | FOR LPAREN declaration expression_statement RPAREN statement
                          | FOR LPAREN declaration expression_statement expression RPAREN statement'''
    # p[0] = Node("iteration_statement", [p[2], p[4]])
    # While loop vale
    if p[1] == "while":
        p[0] = Node("iteration_statement", [p[1], p[3],p[5]])
    # Do while loop vale
    elif p[1] == 'do':
        p[0] = Node("iteration_statement", [p[1],p[2],p[3],p[5]])
    # For loop vale
    elif p[1] == 'for':
        if len(p) == 7:
            p[0] = Node("iteration_statement", [p[1], p[3], p[4],p[6]])
        else:
            p[0] = Node("iteration_statement", [p[1], p[3], p[4],p[5],p[7]])

def p_jump_statement(p):
    '''jump_statement : GOTO IDENTIFIER SEMICOLON
                     | CONTINUE SEMICOLON
                     | BREAK SEMICOLON
                     | RETURN SEMICOLON
                     | RETURN expression SEMICOLON'''
    if len(p) == 3:
        p[0] = Node("jump_statement", [p[1]])
    elif len(p) == 4:
        p[0] = Node("jump_statement", [p[1], p[2]])


# Function definitions
def p_function_definition(p):
    '''function_definition : declaration_specifiers declarator declaration_list compound_statement
                           | declaration_specifiers declarator compound_statement'''
    p[0] = Node("function_definition", [p[1], p[2], p[3]])


def p_declaration_list(p):
    '''declaration_list : declaration
	                    | declaration_list declaration'''
    if len(p) == 2:
        p[0] = Node("declaration_list", [p[1]])
    else:
        p[0] = Node("declaration_list", [p[1], p[2]])


# Error handling
def p_error(p):
    if p:
        print(f"Syntax error at '{p}' (line {p.lineno}): {lines[p.lineno - 1]}")
    else:
        print("Syntax error at EOF")


parser = yacc.yacc()
testcases_dir = './testcases'
# Iterate over all files in the directory
# for filename in os.listdir(testcases_dir):
#     filepath = os.path.join(testcases_dir, filename)
#     if os.path.isfile(filepath):
#         with open(filepath, 'r') as file:
#             data = file.read()
#         print(f"Parsing file: {filepath}")
#         lines = data.split('\n')

#         parser.parse(data)
data = r'''
/* Pure C Code Stress Test (No Preprocessor Processing) */

/* Structures, Unions, and Enumerations */
struct S1 {
    int a;
    double b;
};

union U1 {
    struct S1 s;
    long l;
};

enum MyEnum {
    VAL1 = 1,
    VAL2 = 2,
    VAL3 = 3
};

/* Typedef for function pointer */
typedef int (*func_ptr)(int, int);

/* Basic arithmetic functions */
int add(int a, int b) {
    return a + b;
}

int multiply(int a, int b) {
    return a * b;
}

/* Functions simulating multiple code constructs */
void one_func(void) {
    /* Function body for one_func */
}

void two_func(void) {
    /* Function body for two_func */
}

void three_func(void) {
    /* Function body for three_func */
}

/* Functions with simple names */
int myfunc1(int x) {
    return x;
}

int test_func(int x) {
    return x * 2;
}

/* Function demonstrating variable-length arrays (VLAs) */
void vla_example(int n) {
    int arr[n];
    int i;
    for (i = 0; i < n; i++) {
        arr[i] = i * i;
    }
    for (i = 0; i < n; i++) {
        /* Process each element (e.g., for debugging or analysis) */
    }
}

/* Function demonstrating pointer casts and void* usage */
void pointer_tricks(void) {
    int x = 10;
    int *p = &x;
    void *vp = (void *)p;
    int *p2 = (int *)vp;
}

/* Structure with bit-fields */
struct BitField {
    unsigned int a : 3;
    unsigned int b : 5;
};

/* Tail-recursive function */
int tail_recursion(int n, int acc) {
    if (n == 0)
        return acc;
    return tail_recursion(n - 1, acc + n);
}

/* Switch-case construct with intentional fallthrough */
void switch_example(int n) {
    switch (n) {
        case 1:
            /* fallthrough intended */
        case 2:
            break;
        default:
            break;
    }
}

/* Inline function (using C99 semantics) */
static inline int inline_function(int a, int b) {
    for(int i = 0;i<n;i++){
        continue;
    }
    return a - b;
}

/* Inline assembly example (GCC-style inline assembly) */
void asm_example(void) {
    __asm__("nop");
}

/* Main function exercising all constructs */
int main(void) {
    int a = 5, b = 10;
    int result;
    int i;

    result = add(a, b);
    result = multiply(a, b);
    result = myfunc1(42);
    result = test_func(21);

    vla_example(5);
    pointer_tricks();

    /* Bit-field variable test */
    struct BitField bf;
    bf.a = 5;
    bf.b = 17;

    result = tail_recursion(10, 0);
    switch_example(1);
    switch_example(3);
    result = inline_function(20, 10);

    /* Array of function pointers */
    // func_ptr functions[2];
    // // functions[0] = add;
    // // functions[1] = multiply;
    // // for (i = 0; i < 2; i++) {
    // //     result = functions[i](a, b);
    // // }

    while (1 == 1) {
         for (int i = 1, j = 1; i <= 100 && j <= 1000; i++) {
             printf("what the fuck is this %d\n%d", i, j);
         }
         break;
    }   

    asm_example();

    one_func();
    two_func();
    three_func();
    if(a){
        func();
    }
    else if(b){
        func2();
    }
    else{
        func3();
    }
    return 0;
}

'''
lines = data.split('\n')
root = parser.parse(data)
# root.traverse()
graph = root.to_graph()
graph.render('ast', format='png', view=True)
# dfs(root)
# level_order(root)
# Optionally process or print the result for each file

