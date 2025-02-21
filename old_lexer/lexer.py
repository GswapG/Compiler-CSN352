import ply.lex as lex
from src.defs.token_defs import *
import os, re
# Track line start positions
line_start_positions = [0]

# Lexer States
states = (
    ('mcomment', 'exclusive'),
)

# Simple Token definitions
t_CHAR = r'(\'.\')|(\'\\.\')'

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

# Keyword matching
def t_KEYWORD(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved_keywords.get(t.value,'IDENTIFIER')    # Check for reserved words
    return t

# String literal matching
def t_STRING(t):
    r'"(\\.|(?!\").)*"'
    t.value = t.value[1:-1]
    t.value = t.value.encode().decode('unicode_escape')
    return t

# Float matching
def t_FLOAT(t):
    r'\d+\.\d*'
    # t.value = float(t.value)
    return t

# Integer matching
def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Assignment Operator matching
def t_ASSIGNMENT(t):
    r'=|\+=|\-=|\*=|/=|%=|&=|\|=|\^=|<<=|>>='
    t.type = assignment_operators.get(t.value)
    return t

# Arithmetic Operator matching
def t_ARITHMETIC_EXCLUDING_INCREMENT(t):
    r'\+\+|\-\-|\*|\/|%|\+|\-'
    t.type = arithmetic_operators.get(t.value)
    return t

# Relational Operator matching
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
    r'&|\||\^|~|<<|>>'
    t.type = bitwise_operators.get(t.value)
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

# Period
def t_PERIOD(t):
    r'\.'
    return t

# Newline handling
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    line_start_positions.append(t.lexpos + len(t.value))

# Error handling
def t_error(t):
    if t.value[0].isdigit():
        print(f"Illegal number format: {t.value}")
        t.lexer.skip(len(t.value))
    else:    
        print(f"Illegal character '{t.value[0]}' at line {t.lineno}, position {t.lexpos}")
        t.lexer.skip(1)

def t_mcomment_error(t):
    print(f"Illegal character '{t.value[0]}' inside comment at line {t.lineno}, position {t.lexpos}")
    t.lexer.skip(1)

# Some utils
def read_c_file(path):
    with open(path, 'r') as f:
        content = f.read()
    return content

def generate_output_table(lexer):
    out = []
    for tok in iter(lexer.token, None):
        # Compute linepos relative to the current line
        current_line_start = next(pos for pos in reversed(line_start_positions) if pos <= tok.lexpos)
        linepos = tok.lexpos - current_line_start
        out.append((tok.value, tok.type, tok.lineno, linepos))
    return out

def test(lexer):
    directory_path = './testcases'
    ret = []
    for file_name in os.listdir(directory_path):
        # Check if the file is a .c file
        if file_name.endswith('.c'):
            file_path = os.path.join(directory_path, file_name)
            test_data = read_c_file(file_path)
            lexer.input(test_data)
            ret.append(generate_output_table(lexer))
    return ret

def pretty_print_testcases(testcases, max_lexeme_length=30):
    """
    Pretty prints the list of test cases in a table format with properly aligned columns.
    
    Args:
        testcases: List of test cases where each test case is a list of tuples (lexeme, token, lineno, linepos).
        max_lexeme_length: Maximum length for lexemes to display. Long lexemes will be truncated to this length.
    """
    
    def escape_repr(lexeme):
        """Returns a raw string representation of lexeme if it contains escape characters."""
        if isinstance(lexeme, str):
            return re.sub(r'[\n\r\t]', lambda m: repr(m.group(0))[1:-1], lexeme)
        return str(lexeme)
    
    for case_idx, testcase in enumerate(testcases, start=1):
        # Calculate column widths dynamically for each test case
        lexeme_width = 0
        token_width = 0
        lineno_width = 8   # Fixed width for line number
        linepos_width = 8  # Fixed width for line position
        
        for lexeme, token, lineno, linepos in testcase:
            lexeme_str = escape_repr(lexeme)  
            lexeme_display = lexeme_str[:max_lexeme_length] + ("..." if len(lexeme_str) > max_lexeme_length else "")
            
            lexeme_width = max(lexeme_width, len(lexeme_display))
            token_width = max(token_width, len(token))
        
        # Print header for each test case
        print(f"\n=== Test Case {case_idx} ===")
        header = f"{'Lexeme'.ljust(lexeme_width)}  {'Token'.ljust(token_width)}  {'Line No.'.rjust(lineno_width)}  {'Line Pos.'.rjust(linepos_width)}"
        print(header)
        print('-' * len(header))
        
        # Print all tokens in the test case
        for lexeme, token, lineno, linepos in testcase:
            lexeme_str = escape_repr(lexeme)
            lexeme_display = lexeme_str[:max_lexeme_length] + ("..." if len(lexeme_str) > max_lexeme_length else "")
            
            print(f"{lexeme_display.ljust(lexeme_width)}  {token.ljust(token_width)}  {str(lineno).rjust(lineno_width)}  {str(linepos).rjust(linepos_width)}")


# Driver to test code
if __name__ == "__main__":
    lexer = lex.lex()
    output_tables = test(lexer)
    pretty_print_testcases(output_tables)
    


