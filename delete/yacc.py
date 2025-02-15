import ply.yacc as yacc 
from lexer import *
from tokens import tokens

start = 'translation_unit'

def p_primary_expression(p):
    '''primary_expression : IDENTIFIER
                          | constant
                          | string
                          | LPAREN expression RPAREN
                          | generic_selection
                          | SEMICOLON
    '''

def p_constant(p):
    '''constant : INTEGER
                | F_CONSTANT
                | ENUMERATION_CONSTANT
                | SEMICOLON
    '''

def p_enumeration_constant(p):
    '''enumeration_constant : IDENTIFIER
                            | SEMICOLON
    '''

def p_string(p):
    '''string : STRING_LITERAL
              | FUNC_NAME
              | SEMICOLON
    '''

def p_generic_selection(p):
    '''generic_selection : GENERIC LPAREN assignment_expression COMMA generic_assoc_list RPAREN
                         | SEMICOLON
    '''

def p_generic_assoc_list(p):
    '''generic_assoc_list : generic_association
                          | generic_assoc_list COMMA generic_association
                          | SEMICOLON
    '''

def p_generic_association(p):
    '''generic_association : type_name COLON assignment_expression
                           | DEFAULT COLON assignment_expression
                           | SEMICOLON
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
                          | LPAREN type_name RPAREN LBRACE initializer_list RBRACE
                          | LPAREN type_name RPAREN LBRACE initializer_list COMMA RBRACE
                          | SEMICOLON
    '''

def p_argument_expression_list(p):
    '''argument_expression_list : assignment_expression
                                | argument_expression_list COMMA assignment_expression
                                | SEMICOLON
    '''

def p_unary_expression(p):
    '''unary_expression : postfix_expression
                        | INC_OP unary_expression
                        | DEC_OP unary_expression
                        | unary_operator cast_expression
                        | SIZEOF unary_expression
                        | SIZEOF LPAREN type_name RPAREN
                        | ALIGNOF LPAREN type_name RPAREN
                        | SEMICOLON
    '''

def p_unary_operator(p):
    '''unary_operator : AND
                      | TIMES
                      | PLUS
                      | MINUS
                      | TILDE
                      | NOT
                      | SEMICOLON
    '''

def p_cast_expression(p):
    '''cast_expression : unary_expression
                       | LPAREN type_name RPAREN cast_expression
                       | SEMICOLON
    '''

def p_multiplicative_expression(p):
    '''multiplicative_expression : cast_expression
                                 | multiplicative_expression TIMES cast_expression
                                 | multiplicative_expression DIVIDE cast_expression
                                 | multiplicative_expression MOD cast_expression
                                 | SEMICOLON
    '''

def p_additive_expression(p):
    '''additive_expression : multiplicative_expression
                           | additive_expression PLUS multiplicative_expression
                           | additive_expression MINUS multiplicative_expression
                           | SEMICOLON
    '''

def p_shift_expression(p):
    '''shift_expression : additive_expression
                        | shift_expression LEFT_OP additive_expression
                        | shift_expression RIGHT_OP additive_expression
                        | SEMICOLON
    '''

def p_relational_expression(p):
    '''relational_expression : shift_expression
                             | relational_expression LT shift_expression
                             | relational_expression GT shift_expression
                             | relational_expression LE_OP shift_expression
                             | relational_expression GE_OP shift_expression
                             | SEMICOLON
    '''

def p_equality_expression(p):
    '''equality_expression : relational_expression
                           | equality_expression EQ_OP relational_expression
                           | equality_expression NE_OP relational_expression
                           | SEMICOLON
    '''

def p_and_expression(p):
    '''and_expression : equality_expression
                      | and_expression AND equality_expression
                      | SEMICOLON
    '''

def p_exclusive_or_expression(p):
    '''exclusive_or_expression : and_expression
                                | exclusive_or_expression XOR and_expression
                                | SEMICOLON
    '''

def p_inclusive_or_expression(p):
    '''inclusive_or_expression : exclusive_or_expression
                               | inclusive_or_expression OR exclusive_or_expression
                               | SEMICOLON
    '''

def p_logical_and_expression(p):
    '''logical_and_expression : inclusive_or_expression
                              | logical_and_expression AND_OP inclusive_or_expression
                              | SEMICOLON
    '''

def p_logical_or_expression(p):
    '''logical_or_expression : logical_and_expression
                             | logical_or_expression OR_OP logical_and_expression
                             | SEMICOLON
    '''

def p_conditional_expression(p):
    '''conditional_expression : logical_or_expression
                              | logical_or_expression QUESTION expression COLON conditional_expression
                              | SEMICOLON
    '''

def p_assignment_expression(p):
    '''assignment_expression : conditional_expression
                            | unary_expression assignment_operator assignment_expression
                            | SEMICOLON
    '''

def p_assignment_operator(p):
    '''assignment_operator : EQUALS
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
                          | SEMICOLON
    '''

def p_expression(p):
    '''expression : assignment_expression
                  | expression COMMA assignment_expression
                  | SEMICOLON
    '''

def p_constant_expression(p):
    '''constant_expression : conditional_expression
                           | SEMICOLON
    '''

def p_declaration(p):
    '''declaration : declaration_specifiers SEMICOLON
                   | declaration_specifiers init_declarator_list SEMICOLON
                   | static_assert_declaration
                   | SEMICOLON
    '''

def p_declaration_specifiers(p):
    '''declaration_specifiers : storage_class_specifier declaration_specifiers
                              | storage_class_specifier
                              | type_specifier declaration_specifiers
                              | type_specifier
                              | type_qualifier declaration_specifiers
                              | type_qualifier
                              | function_specifier declaration_specifiers
                              | function_specifier
                              | alignment_specifier declaration_specifiers
                              | alignment_specifier
                              | SEMICOLON
    '''

def p_init_declarator_list(p):
    '''init_declarator_list : init_declarator
                            | init_declarator_list COMMA init_declarator
                            | SEMICOLON
    '''

def p_init_declarator(p):
    '''init_declarator : declarator EQUALS initializer
                       | declarator
                       | SEMICOLON
    '''

def p_storage_class_specifier(p):
    '''storage_class_specifier : TYPEDEF
                               | EXTERN
                               | STATIC
                               | THREAD_LOCAL
                               | AUTO
                               | REGISTER
                               | SEMICOLON
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
                      | BOOL
                      | COMPLEX
                      | IMAGINARY
                      | atomic_type_specifier
                      | struct_or_union_specifier
                      | enum_specifier
                      | SEMICOLON
    '''

def p_struct_or_union_specifier(p):
    '''struct_or_union_specifier : struct_or_union LBRACE struct_declaration_list RBRACE
                                 | struct_or_union IDENTIFIER LBRACE struct_declaration_list RBRACE
                                 | struct_or_union IDENTIFIER
                                 | SEMICOLON
    '''

def p_struct_or_union(p):
    '''struct_or_union : STRUCT
                       | UNION
                       | SEMICOLON
    '''

def p_struct_declaration_list(p):
    '''struct_declaration_list : struct_declaration
                               | struct_declaration_list struct_declaration
                               | SEMICOLON
    '''

def p_struct_declaration(p):
    '''struct_declaration : specifier_qualifier_list SEMICOLON
                          | specifier_qualifier_list struct_declarator_list SEMICOLON
                          | static_assert_declaration
                          | SEMICOLON
    '''

def p_specifier_qualifier_list(p):
    '''specifier_qualifier_list : type_specifier specifier_qualifier_list
                                | type_specifier
                                | type_qualifier specifier_qualifier_list
                                | type_qualifier
                                | SEMICOLON
    '''

def p_struct_declarator_list(p):
    '''struct_declarator_list : struct_declarator
                              | struct_declarator_list COMMA struct_declarator
                              | SEMICOLON
    '''

def p_struct_declarator(p):
    '''struct_declarator : COLON constant_expression
                         | declarator COLON constant_expression
                         | declarator
                         | SEMICOLON
    '''

def p_enum_specifier(p):
    '''enum_specifier : ENUM LBRACE enumerator_list RBRACE
                      | ENUM LBRACE enumerator_list COMMA RBRACE
                      | ENUM IDENTIFIER LBRACE enumerator_list RBRACE
                      | ENUM IDENTIFIER LBRACE enumerator_list COMMA RBRACE
                      | ENUM IDENTIFIER
                      | SEMICOLON
    '''

def p_enumerator_list(p):
    '''enumerator_list : enumerator
                       | enumerator_list COMMA enumerator
                       | SEMICOLON
    '''

def p_enumerator(p):
    '''enumerator : enumeration_constant EQUALS constant_expression
                  | enumeration_constant
                  | SEMICOLON
    '''

def p_atomic_type_specifier(p):
    '''atomic_type_specifier : ATOMIC LPAREN type_name RPAREN
                             | SEMICOLON
    '''

def p_type_qualifier(p):
    '''type_qualifier : CONST
                      | RESTRICT
                      | VOLATILE
                      | ATOMIC
                      | SEMICOLON
    '''

def p_function_specifier(p):
    '''function_specifier : INLINE
                          | NORETURN
                          | SEMICOLON
    '''

def p_alignment_specifier(p):
    '''alignment_specifier : ALIGNAS LPAREN type_name RPAREN
                           | ALIGNAS LPAREN constant_expression RPAREN
                           | SEMICOLON
    '''

def p_declarator(p):
    '''declarator : pointer direct_declarator
                  | direct_declarator
                  | SEMICOLON
    '''

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
                         | SEMICOLON
    '''

def p_pointer(p):
    '''pointer : TIMES type_qualifier_list pointer
               | TIMES type_qualifier_list
               | TIMES pointer
               | TIMES
               | SEMICOLON
    '''

def p_type_qualifier_list(p):
    '''type_qualifier_list : type_qualifier
                           | type_qualifier_list type_qualifier
                           | SEMICOLON
    '''

def p_parameter_type_list(p):
    '''parameter_type_list : parameter_list COMMA ELLIPSIS
                           | parameter_list
                           | SEMICOLON
    '''

def p_parameter_list(p):
    '''parameter_list : parameter_declaration
                      | parameter_list COMMA parameter_declaration
                      | SEMICOLON
    '''

def p_parameter_declaration(p):
    '''parameter_declaration : declaration_specifiers declarator
                              | declaration_specifiers abstract_declarator
                              | declaration_specifiers
                              | SEMICOLON
    '''

def p_identifier_list(p):
    '''identifier_list : IDENTIFIER
                       | identifier_list COMMA IDENTIFIER
                       | SEMICOLON
    '''

def p_type_name(p):
    '''type_name : specifier_qualifier_list abstract_declarator
                 | specifier_qualifier_list
                 | SEMICOLON
    '''

def p_abstract_declarator(p):
    '''abstract_declarator : pointer direct_abstract_declarator
                           | pointer
                           | direct_abstract_declarator
                           | SEMICOLON
    '''

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
                                  | direct_abstract_declarator LPAREN parameter_type_list RPAREN
                                  | SEMICOLON
    '''

def p_initializer(p):
    '''initializer : LBRACE initializer_list RBRACE
                   | LBRACE initializer_list COMMA RBRACE
                   | assignment_expression
                   | SEMICOLON
    '''

def p_initializer_list(p):
    '''initializer_list : designation initializer
                        | initializer
                        | initializer_list COMMA designation initializer
                        | initializer_list COMMA initializer
                        | SEMICOLON
    '''

def p_designation(p):
    '''designation : designator_list EQUALS
                   | SEMICOLON
    '''

def p_designator_list(p):
    '''designator_list : designator
                       | designator_list designator
                       | SEMICOLON
    '''

def p_designator(p):
    '''designator : LBRACKET constant_expression RBRACKET
                  | DOT IDENTIFIER
                  | SEMICOLON
    '''

def p_static_assert_declaration(p):
    '''static_assert_declaration : STATIC_ASSERT LPAREN constant_expression COMMA STRING_LITERAL RPAREN SEMICOLON
                                 | SEMICOLON
    '''

def p_statement(p):
    '''statement : labeled_statement
                 | compound_statement
                 | expression_statement
                 | selection_statement
                 | iteration_statement
                 | jump_statement
                 | SEMICOLON
    '''

def p_labeled_statement(p):
    '''labeled_statement : IDENTIFIER COLON statement
                         | CASE constant_expression COLON statement
                         | DEFAULT COLON statement
                         | SEMICOLON
    '''

def p_compound_statement(p):
    '''compound_statement : LBRACE RBRACE
                          | LBRACE block_item_list RBRACE
                          | SEMICOLON
    '''

def p_block_item_list(p):
    '''block_item_list : block_item
                       | block_item_list block_item
                       | SEMICOLON
    '''

def p_block_item(p):
    '''block_item : declaration
                  | statement
                  | SEMICOLON
    '''

    print(p[0], p[1])

def p_expression_statement(p):
    '''expression_statement : SEMICOLON
                            | expression SEMICOLON
    '''

def p_selection_statement(p):
    '''selection_statement : IF LPAREN expression RPAREN statement ELSE statement
                           | IF LPAREN expression RPAREN statement
                           | SWITCH LPAREN expression RPAREN statement
                           | SEMICOLON
    '''

def p_iteration_statement(p):
    '''iteration_statement : WHILE LPAREN expression RPAREN statement
                           | DO statement WHILE LPAREN expression RPAREN SEMICOLON
                           | FOR LPAREN expression_statement expression_statement RPAREN statement
                           | FOR LPAREN expression_statement expression_statement expression RPAREN statement
                           | FOR LPAREN declaration expression_statement RPAREN statement
                           | FOR LPAREN declaration expression_statement expression RPAREN statement
                           | SEMICOLON
    '''

def p_jump_statement(p):
    '''jump_statement : GOTO IDENTIFIER SEMICOLON
                      | CONTINUE SEMICOLON
                      | BREAK SEMICOLON
                      | RETURN SEMICOLON
                      | RETURN expression SEMICOLON
                      | SEMICOLON
    '''

def p_translation_unit(p):
    '''translation_unit : external_declaration
                        | translation_unit external_declaration
                        | SEMICOLON
    '''
    print(p[0], p[1])

def p_external_declaration(p):
    '''external_declaration : function_definition
                            | declaration
                            | SEMICOLON
    '''

def p_function_definition(p):
    '''function_definition : declaration_specifiers declarator declaration_list compound_statement
                           | declaration_specifiers declarator compound_statement
                           | SEMICOLON
    '''

def p_declaration_list(p):
    '''declaration_list : declaration
                        | declaration_list declaration
                        | SEMICOLON
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