import ply.lex as lex 
from .tokens import *
from .exceptions import *
typedef_names = set()
line_start_positions = [0]

# Lexer states
states = (
    ('mcomment', 'exclusive'),
    ('mstring', 'exclusive')
)

# Simple tokens
t_CHAR_CONSTANT = r'(\'.\')|(\'\\.\')'

# Ignored characters
t_ignore = ' \t'
t_mcomment_ignore = ' \t'
t_mstring_ignore = '' 

# Multiline comment
def t_mcomment(t):
    r'/\*'
    t.lexer.begin('mcomment')

def t_mcomment_end(t):
    r'\*/'
    t.lexer.begin('INITIAL')

def t_mcomment_body(t):
    r'(.|\n)*?(?=\*/)'
    t.lexer.lineno += t.value.count('\n')  
    pass

# Single-line comment
def t_COMMENT(t):
    r'((//)|\#).*'
    pass

# Keyword matching
def t_KEYWORD(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    if t.value in typedef_names:
        t.type = 'TYPEDEF_NAME'
    else:
        t.type = reserved_keywords.get(t.value,'IDENTIFIER')    # Check for reserved words
    return t

# String literal matching
# def t_STRING(t):
#     r'\"([^\\\n]|(\\.))*?\"'
#     # t.value = t.value[1:-1]
#     # adding quotes in string literals
#     t.type = 'STRING_LITERAL'
#     t.value = t.value.encode().decode('unicode_escape')
#     return t
def t_mstring_end(t):
    r'\"'
    t.value = '"' + t.lexer.lexdata[t.lexer.code_start:t.lexer.lexpos-1] + '"'
    print(t.value)
    t.type = "STRING_LITERAL"
    t.lexer.begin('INITIAL')
    return t

def t_mstring(t):
    r'\"'
    t.lexer.begin('mstring')
    t.lexer.code_start = t.lexer.lexpos

def t_mstring_body(t):
    r'[^"\n]+'

# Float matching
def t_FLOAT(t):
    r'\d+\.\d*[f]?'
    t.type = 'F_CONSTANT'
    fl = t.value
    if(fl[-1] == 'f'):
        fl = fl[:-1]
    t.value = float(fl)
    return t

# Integer matching
def t_INTEGER(t):
    r'\d+[LU]?'
    t.type = 'I_CONSTANT'
    integer = t.value
    if(integer[-1] == 'L'):
        integer = integer[:-1]
    t.value = int(integer)
    return t

# Bitwise Assignment Operator matching
def t_BITWISE_ASSIGNMENT(t):
    r'&=|\|=|\^=|<<=|>>='
    t.type = assignment_operators.get(t.value)
    return t

# Relational Operator matching

def t_PTR_OP(t):
    r'\->'
    return t

def t_BITWISE_SHIFT(t):
    r'<<|>>'
    t.type = bitwise_operators.get(t.value)
    return t

def t_RELATIONAL(t):
    r'==|!=|>=|<=|>|<'
    t.type = relational_operators.get(t.value)
    return t

# Logical Operator matching
def t_LOGICAL(t):
    r'&&|\|\||!'
    t.type = logical_operators.get(t.value)
    return t

    # Bitwise Operator matching
def t_BITWISE(t):
    r'&|\||\^|~'
    t.type = bitwise_operators.get(t.value)
    return t

# Assignment Operator matching
def t_ASSIGNMENT(t):
    r'=|\+=|\-=|\*=|/=|%='
    t.type = assignment_operators.get(t.value)
    return t

# Arithmetic Operator matching
def t_ARITHMETIC_EXCLUDING_INCREMENT(t):
    r'\+\+|\-\-|\*|\/|%|\+|\-'
    t.type = arithmetic_operators.get(t.value)
    return t

def t_TERNARY(t):
    r'\?|\:'
    t.type = ternary_operators.get(t.value)
    return t

# Parentheses
def t_LPAREN(t):
    r'\('
    return t

def t_RPAREN(t):
    r'\)'
    return t

# Curly Braces
def t_LBRACE(t):
    r'\{'
    return t

def t_RBRACE(t):
    r'\}'
    return t

# Square Brackets
def t_LBRACKET(t):
    r'\['
    return t

def t_RBRACKET(t):
    r'\]'
    return t

# Semicolon
def t_SEMICOLON(t):
    r';'
    return t

# Comma
def t_COMMA(t):
    r','
    return t

def t_ELLIPSIS(t):
    r'\.\.\.'
    return t
# Period
def t_DOT(t):
    r'\.'
    return t

# Newline handling
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    line_start_positions.append(t.lexpos + len(t.value))

# Error handling
def t_error(t):
    current_line_start = next(pos for pos in reversed(line_start_positions) if pos <= t.lexpos)
    linepos = t.lexpos - current_line_start
    error = f"Illegal character '{t.value[0]}' at line {t.lineno}, position {linepos}"
    reset(t.lexer)
    reset(t.lexer)
    raise CompileException(error)

def t_mcomment_error(t):
    current_line_start = next(pos for pos in reversed(line_start_positions) if pos <= t.lexpos)
    linepos = t.lexpos - current_line_start
    error = f"Illegal character '{t.value[0]}' inside comment at line {t.lineno}, position {linepos}"
    reset(t.lexer)
    reset(t.lexer)
    raise CompileException(error)

def t_mstring_error(t):
    current_line_start = next(pos for pos in reversed(line_start_positions) if pos <= t.lexpos)
    linepos = t.lexpos - current_line_start
    error = f"Illegal character 'newline' inside string at line {t.lineno}, position {linepos}"
    reset(t.lexer)
    reset(t.lexer)
    raise CompileException(error)

def reset(le):
    le.input('')
    le.begin('INITIAL')

lexer = lex.lex()