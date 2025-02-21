import ply.yacc as yacc 
from lexer import *
from tokens import tokens

def p_expression_binop(p):
    '''expression : expression PLUS expression
                    | expression MINUS expression
                    | expression MULTIPLY expression
                    | expression DIVIDE expression'''
    if p[2] == '+': p[0] = p[1] + p[3]
    elif p[2] == '-': p[0] = p[1] - p[3]
    elif p[2] == '*': p[0] = p[1] * p[3]
    elif p[2] == '/': p[0] = p[1] / p[3]

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_number(p):
    'expression : INTEGER'
    p[0] = p[1]

def p_error(p):
    print("Syntax error!")

parser = yacc.yacc() 

while True:
    try:
        s = input("Enter expression: ")
    except EOFError:
        break
    if not s:
        continue
    result = parser.parse(s)
    print(result)