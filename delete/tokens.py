# Reserved Keywords Dictionary
reserved_keywords = {
    'auto': 'AUTO',
    'break': 'BREAK',
    'case': 'CASE',
    'char': 'CHAR',
    'const': 'CONST',
    'continue': 'CONTINUE',
    'default': 'DEFAULT',
    'do': 'DO',
    'double': 'DOUBLE',
    'else': 'ELSE',
    'enum': 'ENUM',
    'extern': 'EXTERN',
    'float': 'FLOAT',
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
    '_Alignas': 'ALIGNAS',
    '_Alignof': 'ALIGNOF',
    '_Atomic': 'ATOMIC',
    '_Bool': 'BOOL',
    '_Complex': 'COMPLEX',
    '_Generic': 'GENERIC',
    '_Imaginary': 'IMAGINARY',
    '_Noreturn': 'NORETURN',
    '_Static_assert': 'STATIC_ASSERT',
    '_Thread_local': 'THREAD_LOCAL'
}

# Arithmetic Operators Dictionary
arithmetic_operators = {
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'TIMES',
    '/': 'DIVIDE',
    '%': 'MOD'
}

# Relational Operators Dictionary
relational_operators = {
    '==': 'EQ_OP',
    '!=': 'NE_OP',
    '>': 'GT',
    '<': 'LT',
    '>=': 'GE_OP',
    '<=': 'LE_OP'
}

# Bitwise Operators Dictionary
bitwise_operators = {
    '&': 'AND',
    '|': 'OR',
    '^': 'XOR',
    '~': 'TILDE',
    '<<': 'LEFT_OP',
    '>>': 'RIGHT_OP'
}

# Logical Operators Dictionary
logical_operators = {
    '&&': 'AND_OP',
    '||': 'OR_OP',
    '!': 'NOT'
}

# Assignment Operators Dictionary
assignment_operators = {
    '=': 'EQUALS',
    '+=': 'ADD_ASSIGN',
    '-=': 'SUB_ASSIGN',
    '*=': 'MUL_ASSIGN',
    '/=': 'DIV_ASSIGN',
    '%=': 'MOD_ASSIGN',
    '<<=': 'LEFT_ASSIGN',
    '>>=': 'RIGHT_ASSIGN',
    '&=': 'AND_ASSIGN',
    '^=': 'XOR_ASSIGN',
    '|=': 'OR_ASSIGN'
}

# Increment/Decrement Operators
inc_dec_operators = {
    '++': 'INC_OP',
    '--': 'DEC_OP'
}

# Ternary Operators Dictionary
ternary_operators = {
    '?': 'QUESTION',
    ':': 'COLON'
}

# Punctuators Dictionary
punctuators = {
    '(': 'LPAREN',
    ')': 'RPAREN',
    '{': 'LBRACE',
    '}': 'RBRACE',
    '[': 'LBRACKET',
    ']': 'RBRACKET',
    ';': 'SEMICOLON',
    ',': 'COMMA',
    '.': 'DOT',
    '...': 'ELLIPSIS'
}

# Other Tokens
other_tokens = {
    'IDENTIFIER': 'IDENTIFIER',
    'I_CONSTANT': 'I_CONSTANT',
    'F_CONSTANT': 'F_CONSTANT',
    'STRING_LITERAL': 'STRING_LITERAL',
    'ENUMERATION_CONSTANT': 'ENUMERATION_CONSTANT',
    'PTR_OP': 'PTR_OP',
    'FUNC_NAME': 'FUNC_NAME'
}

# Combine all tokens into a single list
tokens = [
    'INTEGER',
] + (
    list(reserved_keywords.values()) +
    list(arithmetic_operators.values()) +
    list(relational_operators.values()) +
    list(bitwise_operators.values()) +
    list(logical_operators.values()) +
    list(assignment_operators.values()) +
    list(inc_dec_operators.values()) +
    list(ternary_operators.values()) +
    list(punctuators.values()) +
    list(other_tokens.values())
)

