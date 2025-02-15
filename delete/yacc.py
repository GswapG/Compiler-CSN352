import ply.yacc as yacc 
from lexer import *
from tokens import tokens

start = 'translation_unit'

precedence = (
    ('left', 'OR_OP'),
    ('left', 'AND_OP'),
    ('left', 'EQ_OP', 'NE_OP'),
    ('left', 'LE_OP', 'GE_OP', 'LEFT_OP', 'RIGHT_OP'),
    ('left', 'ADD_ASSIGN', 'SUB_ASSIGN'),
    ('left', 'MUL_ASSIGN', 'DIV_ASSIGN', 'MOD_ASSIGN'),
    ('right', 'PTR_OP', 'INC_OP', 'DEC_OP'),
    ('right', 'MINUS', 'PLUS', 'NOT', 'SIZEOF'),
)

def p_primary_expression(p):
    '''primary_expression : IDENTIFIER
                          | CONSTANT
                          | STRING_LITERAL
                          | LPAREN expression RPAREN
    '''

def p_postfix_expression(p):
    '''postfix_expression : primary_expression
                           | postfix_expression LBRACKET expression RBRACKET
                           | postfix_expression LPAREN RPAREN
                           | postfix_expression LPAREN argument_expression_list RPAREN
                           | postfix_expression DOT IDENTIFIER
                           | postfix_expression PTR_OP IDENTIFIER
                           | postfix_expression INC_OP
                           | postfix_expression DEC_OP
    '''

def p_argument_expression_list(p):
    '''argument_expression_list : assignment_expression
                                 | argument_expression_list COMMA assignment_expression
    '''

def p_unary_expression(p):
    '''unary_expression : postfix_expression
                        | INC_OP unary_expression
                        | DEC_OP unary_expression
                        | unary_operator cast_expression
                        | SIZEOF unary_expression
                        | SIZEOF LPAREN type_name RPAREN
    '''

def p_unary_operator(p):
    '''unary_operator : AND
                      | TIMES
                      | PLUS
                      | MINUS
                      | TILDE
                      | NOT
    '''

def p_cast_expression(p):
    '''cast_expression : unary_expression
                       | LPAREN type_name RPAREN cast_expression
    '''

def p_multiplicative_expression(p):
    '''multiplicative_expression : cast_expression
                                 | multiplicative_expression TIMES cast_expression
                                 | multiplicative_expression DIVIDE cast_expression
                                 | multiplicative_expression MOD cast_expression
    '''

def p_additive_expression(p):
    '''additive_expression : multiplicative_expression
                           | additive_expression PLUS multiplicative_expression
                           | additive_expression MINUS multiplicative_expression
    '''

def p_shift_expression(p):
    '''shift_expression : additive_expression
                        | shift_expression LEFT_OP additive_expression
                        | shift_expression RIGHT_OP additive_expression
    '''

def p_relational_expression(p):
    '''relational_expression : shift_expression
                             | relational_expression LT shift_expression
                             | relational_expression GT shift_expression
                             | relational_expression LE_OP shift_expression
                             | relational_expression GE_OP shift_expression
    '''

def p_equality_expression(p):
    '''equality_expression : relational_expression
                           | equality_expression EQ_OP relational_expression
                           | equality_expression NE_OP relational_expression
    '''

def p_and_expression(p):
    '''and_expression : equality_expression
                      | and_expression AND equality_expression
    '''

def p_exclusive_or_expression(p):
    '''exclusive_or_expression : and_expression
                               | exclusive_or_expression XOR and_expression
    '''

def p_inclusive_or_expression(p):
    '''inclusive_or_expression : exclusive_or_expression
                               | inclusive_or_expression OR exclusive_or_expression
    '''

def p_logical_and_expression(p):
    '''logical_and_expression : inclusive_or_expression
                              | logical_and_expression AND_OP inclusive_or_expression
    '''

def p_logical_or_expression(p):
    '''logical_or_expression : logical_and_expression
                             | logical_or_expression OR_OP logical_and_expression
    '''

def p_conditional_expression(p):
    '''conditional_expression : logical_or_expression
                               | logical_or_expression QUESTION expression COLON conditional_expression
    '''

def p_assignment_expression(p):
    '''assignment_expression : conditional_expression
                             | unary_expression assignment_operator assignment_expression
    '''

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
                           | OR_ASSIGN
    '''

def p_expression(p):
    '''expression : assignment_expression
                  | expression COMMA assignment_expression
    '''

def p_constant_expression(p):
    '''constant_expression : conditional_expression
    '''

def p_declaration(p):
    '''declaration : declaration_specifiers SEMICOLON
                   | declaration_specifiers init_declarator_list SEMICOLON
    '''

def p_declaration_specifiers(p):
    '''declaration_specifiers : storage_class_specifier
                              | storage_class_specifier declaration_specifiers
                              | type_specifier
                              | type_specifier declaration_specifiers
                              | type_qualifier
                              | type_qualifier declaration_specifiers
    '''

def p_init_declarator_list(p):
    '''init_declarator_list : init_declarator
                            | init_declarator_list COMMA init_declarator
    '''

def p_init_declarator(p):
    '''init_declarator : declarator
                       | declarator ASSIGN initializer
    '''

def p_storage_class_specifier(p):
    '''storage_class_specifier : TYPEDEF
                               | EXTERN
                               | STATIC
                               | AUTO
                               | REGISTER
    '''

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
                      | struct_or_union_specifier
                      | enum_specifier
                      | TYPE_NAME
    '''

def p_struct_or_union_specifier(p):
    '''struct_or_union_specifier : struct_or_union IDENTIFIER LBRACE struct_declaration_list RBRACE
                                  | struct_or_union LBRACE struct_declaration_list RBRACE
                                  | struct_or_union IDENTIFIER
    '''

def p_struct_or_union(p):
    '''struct_or_union : STRUCT
                       | UNION
    '''

def p_struct_declaration_list(p):
    '''struct_declaration_list : struct_declaration
                               | struct_declaration_list struct_declaration
    '''

def p_struct_declaration(p):
    '''struct_declaration : specifier_qualifier_list struct_declarator_list SEMICOLON
    '''

def p_specifier_qualifier_list(p):
    '''specifier_qualifier_list : type_specifier specifier_qualifier_list
                                | type_specifier
                                | type_qualifier specifier_qualifier_list
                                | type_qualifier
    '''

def p_struct_declarator_list(p):
    '''struct_declarator_list : struct_declarator
                              | struct_declarator_list COMMA struct_declarator
    '''

def p_struct_declarator(p):
    '''struct_declarator : declarator
                         | COLON constant_expression
                         | declarator COLON constant_expression
    '''

def p_enum_specifier(p):
    '''enum_specifier : ENUM LBRACE enumerator_list RBRACE
                       | ENUM IDENTIFIER LBRACE enumerator_list RBRACE
                       | ENUM IDENTIFIER
    '''

def p_enumerator_list(p):
    '''enumerator_list : enumerator
                       | enumerator_list COMMA enumerator
    '''

def p_enumerator(p):
    '''enumerator : IDENTIFIER
                  | IDENTIFIER ASSIGN constant_expression
    '''

def p_type_qualifier(p):
    '''type_qualifier : CONST
                      | VOLATILE
    '''

def p_declarator(p):
    '''declarator : pointer direct_declarator
                  | direct_declarator
    '''

def p_direct_declarator(p):
    '''direct_declarator : IDENTIFIER
                         | LPAREN declarator RPAREN
                         | direct_declarator LBRACKET constant_expression RBRACKET
                         | direct_declarator LBRACKET RBRACKET
                         | direct_declarator LPAREN parameter_type_list RPAREN
                         | direct_declarator LPAREN identifier_list RPAREN
                         | direct_declarator LPAREN RPAREN
    '''

def p_pointer(p):
    '''pointer : TIMES
               | TIMES type_qualifier_list
               | TIMES pointer
               | TIMES type_qualifier_list pointer
    '''

def p_type_qualifier_list(p):
    '''type_qualifier_list : type_qualifier
                           | type_qualifier_list type_qualifier
    '''

def p_parameter_type_list(p):
    '''parameter_type_list : parameter_list
                           | parameter_list COMMA ELLIPSIS
    '''

def p_parameter_list(p):
    '''parameter_list : parameter_declaration
                      | parameter_list COMMA parameter_declaration
    '''

def p_parameter_declaration(p):
    '''parameter_declaration : declaration_specifiers declarator
                             | declaration_specifiers abstract_declarator
                             | declaration_specifiers
    '''

def p_identifier_list(p):
    '''identifier_list : IDENTIFIER
                       | identifier_list COMMA IDENTIFIER
    '''

def p_type_name(p):
    '''type_name : specifier_qualifier_list
                 | specifier_qualifier_list abstract_declarator
    '''

def p_abstract_declarator(p):
    '''abstract_declarator : pointer
                           | direct_abstract_declarator
                           | pointer direct_abstract_declarator
    '''

def p_direct_abstract_declarator(p):
    '''direct_abstract_declarator : LPAREN abstract_declarator RPAREN
                                  | LBRACKET RBRACKET
                                  | LBRACKET constant_expression RBRACKET
                                  | direct_abstract_declarator LBRACKET RBRACKET
                                  | direct_abstract_declarator LBRACKET constant_expression RBRACKET
                                  | LPAREN RPAREN
                                  | LPAREN parameter_type_list RPAREN
                                  | direct_abstract_declarator LPAREN RPAREN
                                  | direct_abstract_declarator LPAREN parameter_type_list RPAREN
    '''

def p_initializer(p):
    '''initializer : assignment_expression
                   | LBRACE initializer_list RBRACE
                   | LBRACE initializer_list COMMA RBRACE
    '''

def p_initializer_list(p):
    '''initializer_list : initializer
                        | initializer_list COMMA initializer
    '''

def p_statement(p):
    '''statement : labeled_statement
                 | compound_statement
                 | expression_statement
                 | selection_statement
                 | iteration_statement
                 | jump_statement
    '''

def p_labeled_statement(p):
    '''labeled_statement : IDENTIFIER COLON statement
                         | CASE constant_expression COLON statement
                         | DEFAULT COLON statement
    '''

def p_compound_statement(p):
    '''compound_statement : LBRACE RBRACE
                          | LBRACE statement_list RBRACE
                          | LBRACE declaration_list RBRACE
                          | LBRACE declaration_list statement_list RBRACE
    '''

def p_declaration_list(p):
    '''declaration_list : declaration
                        | declaration_list declaration
    '''

def p_statement_list(p):
    '''statement_list : statement
                      | statement_list statement
    '''

def p_expression_statement(p):
    '''expression_statement : SEMICOLON
                            | expression SEMICOLON
    '''

def p_selection_statement(p):
    '''selection_statement : IF LPAREN expression RPAREN statement
                           | IF LPAREN expression RPAREN statement ELSE statement
                           | SWITCH LPAREN expression RPAREN statement
    '''

def p_iteration_statement(p):
    '''iteration_statement : WHILE LPAREN expression RPAREN statement
                           | DO statement WHILE LPAREN expression RPAREN SEMICOLON
                           | FOR LPAREN expression_statement expression_statement RPAREN statement
                           | FOR LPAREN expression_statement expression_statement expression RPAREN statement
    '''

def p_jump_statement(p):
    '''jump_statement : GOTO IDENTIFIER SEMICOLON
                      | CONTINUE SEMICOLON
                      | BREAK SEMICOLON
                      | RETURN SEMICOLON
                      | RETURN expression SEMICOLON
    '''

def p_translation_unit(p):
    '''translation_unit : external_declaration
                        | translation_unit external_declaration
    '''

def p_external_declaration(p):
    '''external_declaration : function_definition
                            | declaration
    '''

def p_function_definition(p):
    '''function_definition : declaration_specifiers declarator declaration_list compound_statement
                           | declaration_specifiers declarator compound_statement
                           | declarator declaration_list compound_statement
                           | declarator compound_statement
    '''

def p_error(p):
    print(p)
    print("Syntax error!")

parser = yacc.yacc() 

while True:
    try:
        s = input("Enter expression: ")
    except EOFError:
        break
    if not s:
        continue
    print(s.encode('unicode-escape'))
    result = parser.parse(s)
    print(result)