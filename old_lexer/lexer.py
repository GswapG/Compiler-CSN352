import ply.lex as lex 
from tokens import *
typedef_names = set()
line_start_positions = [0]

# Lexer states
states = (
    ('mcomment', 'exclusive'),
)

# Simple tokens
t_CHAR_CONSTANT = r'(\'.\')|(\'\\.\')'

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

# Single-line comment
def t_COMMENT(t):
    r'//.*'
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
def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    # t.value = t.value[1:-1]
    # adding quotes in string literals
    t.type = 'STRING_LITERAL'
    t.value = t.value.encode().decode('unicode_escape')
    return t

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
    t.lexer.skip(1)

def t_mcomment_error(t):
    current_line_start = next(pos for pos in reversed(line_start_positions) if pos <= t.lexpos)
    linepos = t.lexpos - current_line_start
    error = f"Illegal character '{t.value[0]}' inside comment at line {t.lineno}, position {linepos}"

    t.lexer.skip(1)

input_code = """
extern int extVar;
_Static_assert(sizeof(int) >= 2, "int too small");

inline int add(int a, int b) {
    return a + b;
}

static int sub(int a, int b) {
    return a - b;
}

/* Structure definition using _Alignas */
struct Node {
    int data;
    struct Node *next;  /* PTR_OP usage */
};

/* Union definition */
union Data {
    int i;
    float f;
};

/* Typedef for union */
typedef union Data DataType;

/* Enumeration definition */
enum Color { RED, GREEN, BLUE };

int color_code(enum Color col) {
    switch(col) {
        case RED:
            return 1;
        case GREEN:
            return 2;
        case BLUE:
            return 3;
        default:
            return 0;
    }
}

/* Function with variable arguments (ellipsis punctuator) */
int varfunc(int count, ...) {
    return count;
}

int main(void) {
    /* Variable declarations using reserved keywords */
    auto int autoVar = 1;
    register int regVar = 2;
    volatile int volVar = 3;
    const int constVar = 4;
    static int staticVar = 5;
    long longVar = 6;
    signed int sInt = -7;
    unsigned int uInt = 8;
    short shortVar = 9;

    /* Other tokens: I_CONSTANT, F_CONSTANT, CHAR_CONSTANT, STRING_LITERAL */
    int a = 10, b = 3;
    float f = 3.14;
    double d = 2.71828;
    char ch = 'A';
    char str[] = "Test String";

    /* _Bool, _Complex, _Imaginary, _Atomic, _Thread_local */
    _Bool flag = 1;
    _Complex float comp = 1.0 + 2.0 * 1.0;
    _Atomic int atomic_var = 0;

    /* _Generic usage */
    const char* type_str = _Generic(a, int: "int", default: "other");

    /* _Alignof and typedef (using unsigned and long) */
    typedef unsigned long my_size_t;

    /* Arithmetic operators */
    int sum = a + b;
    int diff = a - b;
    int prod = a * b;
    int quot = a / b;
    int rem = a % b;
    a++;
    b--;

    /* Relational operators */
    if(a == b) { }
    if(a != b) { }
    if(a > b) { }
    if(a < b) { }
    if(a >= b) { }
    if(a <= b) { }

    /* if-else statement */
    if(a < b) {
        a = b;
    } else {
        a = a;
    }

    /* Bitwise operators */
    int bw_and = a & b;
    int bw_or = a | b;
    int bw_xor = a ^ b;
    int bw_tilde = ~a;
    int bw_left = a << 2;
    int bw_right = a >> 2;

    /* Logical operators */
    if(a && b) { }
    if(a || b) { }
    if(!a) { }

    /* Assignment operators */
    a = 5;
    a += 2;
    a -= 1;
    a *= 3;
    a /= 2;
    a %= 2;
    a <<= 1;
    a >>= 1;
    a &= 3;
    a ^= 2;
    a |= 1;

    /* Ternary operator */
    int c = (a > b) ? a : b;

    /* Loop constructs: for, while, and do-until (using reserved "until") */
    int i;
    for(i = 0; i < 5; i++) {
        if(i == 2)
            continue;
        if(i == 4)
            break;
    }
    
    int j = 0;
    while(j < 5) {
        j++;
    }
    
    int k = 5;
    do {
        k--;
    } until(k == 0);

    /* Switch-case with enumeration constants */
    enum Color color = RED;
    int code = color_code(color);
    if(code == 0) {
        goto error;
    }

    /* Structure and pointer usage (PTR_OP) */
    struct Node node;
    struct Node *pnode = &node;
    pnode->data = 100;

    /* Using restrict with a pointer */
    int * restrict ptr = &a;

    /* Function calls using FUNC_NAME tokens */
    int result1 = add(a, b);
    int result2 = sub(a, b);
    int var_res = varfunc(3, a, b, c);

    return 0;
error:
    return 1;
}
"""
lexer = lex.lex()

# Provide input to the lexer
lexer.input(input_code)

# Iterate over the tokens and print the lexer table
print("Token Type\t\tValue\t\tLine\t\tPosition")
print("-------------------------------------------------------------")
while True:
    tok = lexer.token()
    if not tok:
        break  # No more input
    print(f"{tok.type}\t\t{tok.value}\t\t{tok.lineno}\t\t{tok.lexpos}")