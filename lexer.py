import ply.lex as lex

reserved_keywords = {
    'auto': 'AUTO',
    'break': 'BREAK',
    'case': 'CASE',
    'char': 'CHARKW',
    'const': 'CONST',
    'continue': 'CONTINUE',
    'default': 'DEFAULT',
    'do': 'DO',
    'double': 'DOUBLE',
    'else': 'ELSE',
    'enum': 'ENUM',
    'extern': 'EXTERN',
    'float': 'FLOATKW',
    'for': 'FOR',
    'goto': 'GOTO',
    'if': 'IF',
    'inline': 'INLINE',
    'int': 'INT',
    'long': 'LONG',
    'register': 'REGISTER',
    'restrict': 'RESTRICT',
    'return': 'RETURN',
    'short': 'SHORT',
    'signed': 'SIGNED',
    'sizeof': 'SIZEOF',
    'static': 'STATIC',
    'struct': 'STRUCT',
    'switch': 'SWITCH',
    'typedef': 'TYPEDEF',
    'union': 'UNION',
    'unsigned': 'UNSIGNED',
    'void': 'VOID',
    'volatile': 'VOLATILE',
    'while': 'WHILE',
    '_Alignas': '_ALIGNAS',
    '_Alignof': '_ALIGNOF',
    '_Atomic': '_ATOMIC',
    '_Bool': '_BOOL',
    '_Complex': '_COMPLEX',
    '_Generic': '_GENERIC',
    '_Imaginary': '_IMAGINARY',
    '_Noreturn': '_NORETURN',
    '_Static_assert': '_STATIC_ASSERT',
    '_Thread_local': '_THREAD_LOCAL'
}


tokens = [
    'INTEGER',
    'FLOAT',
    'IDENTIFIER',
    'CHAR',
    'STRING',
    'ARITHOP',
    'RELOP',
    'ASNMT',
] + list(reserved_keywords.values())

# Lexer States
states = (
    ('mcomment', 'exclusive'),
)

# Token definitions
t_INTEGER = r'\d+'
t_CHAR = r'\'.\''

# Ignored characters
t_ignore = ' \t'
t_mcomment_ignore = ' \t'  

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

# Single-line comments
def t_COMMENT(t):
    r'//.*'
    pass

# Newline handling
def t_newline(t):
    r'\n+'
    t.lexer.lineno += 1

# Keyword matching

def t_KEYWORD(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved_keywords.get(t.value,'IDENTIFIER')    # Check for reserved words
    return t

# Error handling
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}, position {t.lexpos}")
    t.lexer.skip(1)

def t_mcomment_error(t):
    print(f"Illegal character '{t.value[0]}' inside comment at line {t.lineno}, position {t.lexpos}")
    t.lexer.skip(1)

# Driver to test code
if __name__ == "__main__":
    lexer = lex.lex()
    test_data = '''//hello
    123  12 3 123 12 
    123123
    int 
    char '2'
    auto 
    /*hello*/'''
    lexer.input(test_data)
    while 1:
        # print('doing something...')
        tok = lexer.token()
        if not tok:
            break
        print(tok, f'; Line number : {lexer.lineno}')
