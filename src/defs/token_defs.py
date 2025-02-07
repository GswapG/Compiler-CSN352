# Reserved Keywords Dictionary
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

# Arithmetic Operators Dictionary
arithmetic_operators = {
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'MULTIPLY',
    '/': 'DIVIDE',
    '%': 'MODULUS',
    '++': 'INCREMENT',
    '--': 'DECREMENT'
}

# Relational Operators Dictionary
relational_operators = {
    '==': 'EQUAL',
    '!=': 'NOT_EQUAL',
    '>': 'GREATER_THAN',
    '<': 'LESS_THAN',
    '>=': 'GREATER_EQUAL',
    '<=': 'LESS_EQUAL'
}

# Bitwise Operators Dictionary
bitwise_operators = {
    '&': 'BITWISE_AND',
    '|': 'BITWISE_OR',
    '^': 'BITWISE_XOR',
    '~': 'BITWISE_NOT',
    '<<': 'LEFT_SHIFT',
    '>>': 'RIGHT_SHIFT'
}

# Logical Operators Dictionary
logical_operators = {
    '&&': 'LOGICAL_AND',
    '||': 'LOGICAL_OR',
    '!': 'LOGICAL_NOT'
}

bitwise_assignment_operators = {
    '&=': 'BITWISE_AND_ASSIGN',
    '|=': 'BITWISE_OR_ASSIGN',
    '^=': 'BITWISE_XOR_ASSIGN',
    '<<=': 'LEFT_SHIFT_ASSIGN',
    '>>=': 'RIGHT_SHIFT_ASSIGN'
}

# Assignment Operators Dictionary
assignment_operators = {
    '=': 'ASSIGN',
    '+=': 'ADD_ASSIGN',
    '-=': 'SUBTRACT_ASSIGN',
    '*=': 'MULTIPLY_ASSIGN',
    '/=': 'DIVIDE_ASSIGN',
    '%=': 'MODULUS_ASSIGN'
}

# Random paranthesis and things like that
punctuators = {

}
tokens = [
    'INTEGER',
    'FLOAT',
    'IDENTIFIER',
    'CHAR',
    'STRING',
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'LBRACKET',
    'RBRACKET',
    'SEMICOLON',
    'COMMA',
    'PERIOD'
] + list(reserved_keywords.values()) \
+ list(arithmetic_operators.values()) \
+ list(relational_operators.values()) \
+ list(bitwise_operators.values()) \
+ list(logical_operators.values()) \
+ list(assignment_operators.values()) \
+ list(bitwise_assignment_operators.values())