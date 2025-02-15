from .ply.lex import lex 
from .defs.token_defs import *
import os, re

class Lexer(object):
    """
    Lexer class for C like language
    -To use this lexer, first create an object and call build() on it.

    -Create a folder 'testcases' in the same directory 
    """

    tokens = tokens
    def __init__(self):
        self.line_start_positions = [0]
        self.lexer = None
        self.error_list = []

    # Lexer states
    states = (
        ('mcomment', 'exclusive'),
    )

    # Simple tokens
    t_CHAR = r'(\'.\')|(\'\\.\')'

    # Ignored characters
    t_ignore = ' \t'
    t_mcomment_ignore = ' \t'  

    # Multiline comment
    def t_mcomment(self, t):
        r'/\*'
        t.lexer.begin('mcomment')

    def t_mcomment_end(self, t):
        r'\*/'
        t.lexer.begin('INITIAL')

    def t_mcomment_body(self, t):
        r'(.|\n)*?(?=\*/)'
        t.lexer.lineno += t.value.count('\n')  
        pass

    # Single-line comment
    def t_COMMENT(self, t):
        r'//.*'
        pass

    # Keyword matching
    def t_KEYWORD(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = reserved_keywords.get(t.value,'IDENTIFIER')    # Check for reserved words
        return t

    # String literal matching
    def t_STRING(self, t):
        r'\"([^\\\n]|(\\.))*?\"'
        # t.value = t.value[1:-1]
        # adding quotes in string literals
        t.type = 'STRING_LITERAL'
        t.value = t.value.encode().decode('unicode_escape')
        return t

    # Float matching
    def t_FLOAT(self, t):
        r'\d+\.\d*'
        t.type = 'CONSTANT'
        t.value = float(t.value)
        return t

    # Integer matching
    def t_INTEGER(self, t):
        r'\d+'
        t.type = 'CONSTANT'
        t.value = int(t.value)
        return t

    # Bitwise Assignment Operator matching
    def t_BITWISE_ASSIGNMENT(self, t):
        r'&=|\|=|\^=|<<=|>>='
        t.type = assignment_operators.get(t.value)
        return t
    
    # Logical Operator matching
    def t_LOGICAL(self, t):
        r'&&|\|\||!'
        t.type = logical_operators.get(t.value)
        return t
    
     # Bitwise Operator matching
    def t_BITWISE(self, t):
        r'&|\||\^|~|<<|>>'
        t.type = bitwise_operators.get(t.value)
        return t
    
    # Relational Operator matching
    def t_RELATIONAL(self, t):
        r'==|!=|>=|<=|>|<'
        t.type = relational_operators.get(t.value)
        return t

    # Assignment Operator matching
    def t_ASSIGNMENT(self, t):
        r'=|\+=|\-=|\*=|/=|%='
        t.type = assignment_operators.get(t.value)
        return t

    # Arithmetic Operator matching
    def t_ARITHMETIC_EXCLUDING_INCREMENT(self, t):
        r'\+\+|\-\-|\*|\/|%|\+|\-'
        t.type = arithmetic_operators.get(t.value)
        return t

    def t_TERNARY(self, t):
        r'\?|\:'
        t.type = ternary_operators.get(t.value)
        return t

    # Parentheses
    def t_LPAREN(self, t):
        r'\('
        return t

    def t_RPAREN(self, t):
        r'\)'
        return t

    # Curly Braces
    def t_LBRACE(self, t):
        r'\{'
        return t

    def t_RBRACE(self, t):
        r'\}'
        return t

    # Square Brackets
    def t_LBRACKET(self, t):
        r'\['
        return t

    def t_RBRACKET(self, t):
        r'\]'
        return t

    # Semicolon
    def t_SEMICOLON(self, t):
        r';'
        return t

    # Comma
    def t_COMMA(self, t):
        r','
        return t

    # Period
    def t_PERIOD(self, t):
        r'\.'
        return t

    # Newline handling
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        self.line_start_positions.append(t.lexpos + len(t.value))

    # Error handling
    def t_error(self, t):
        current_line_start = next(pos for pos in reversed(self.line_start_positions) if pos <= t.lexpos)
        linepos = t.lexpos - current_line_start
        error = f"Illegal character '{t.value[0]}' at line {t.lineno}, position {linepos}"
        self.error_list.append(error)
        t.lexer.skip(1)

    def t_mcomment_error(self, t):
        current_line_start = next(pos for pos in reversed(self.line_start_positions) if pos <= t.lexpos)
        linepos = t.lexpos - current_line_start
        error = f"Illegal character '{t.value[0]}' inside comment at line {t.lineno}, position {linepos}"
        self.error_list.append(error)
        t.lexer.skip(1)

    def build(self,**kwargs):
        self.lexer = lex(module=self, **kwargs)

    def read_c_file(self,path):
        with open(path, 'r') as f:
            content = f.read()
        return content

    def generate_output_table(self):
        out = []
        for tok in iter(self.lexer.token, None):
            # Compute linepos relative to the current line
            current_line_start = next(pos for pos in reversed(self.line_start_positions) if pos <= tok.lexpos)
            linepos = tok.lexpos - current_line_start
            out.append((tok.value, tok.type, tok.lineno, linepos))
        return out

    def test(self):
        directory_path = './testcases'
        ret = []
        test_files = os.listdir(directory_path)
        test_files.sort()
        for file_name in test_files:
            self.lexer.lineno = 0
            # Check if the file is a .c file
            if file_name.endswith('.c'):
                file_path = os.path.join(directory_path, file_name)
                test_data = self.read_c_file(file_path)
                self.lexer.input(test_data)

                output_table = self.generate_output_table()
                error_table = self.error_list

                self.error_list = []
                ret.append((output_table, error_table))
        return ret

    def pretty_print_testcases(self,testcases, max_lexeme_length=30):
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
        
        total_line = 0
        for case_idx, table in enumerate(testcases, start=1):
            file_line = 0
            # Calculate column widths dynamically for each test case
            lexeme_width = max_lexeme_length
            token_width = max_lexeme_length
            lineno_width = 10   # Fixed width for line number
            linepos_width = 10  # Fixed width for line position

            output_table = table[0]
            error_table = table[1]
            
            # for lexeme, token, lineno, linepos in output_table:
            #     lexeme_str = escape_repr(lexeme)  
            #     lexeme_display = lexeme_str[:max_lexeme_length] + ("..." if len(lexeme_str) > max_lexeme_length else "")
                
            #     lexeme_width = max(lexeme_width, len(lexeme_display))
            #     token_width = max(token_width, len(token))
            
            # Print header for each test case
            format_length = (126 - len(f"  Test Case {case_idx}  ")) // 2
            print(f"\n{'='*(format_length)}  Test Case {case_idx}  {'='*(format_length)}")
            header = f"{'Lexeme'.ljust(lexeme_width)}  {'Token'.ljust(token_width)}  {'Line No.'.ljust(lineno_width)}  {'Line Pos.'.ljust(linepos_width)}"
            print(header)
            print('-' * len(header))
            
            # Print all tokens in the test case
            for lexeme, token, lineno, linepos in output_table:
                lexeme_str = escape_repr(lexeme)
                lexeme_display = lexeme_str[:max_lexeme_length-3] + ("..." if len(lexeme_str) > max_lexeme_length else "")
                
                print(f"{lexeme_display.ljust(lexeme_width)}  {str(token).ljust(token_width)}  {str(lineno).ljust(lineno_width)}  {str(linepos).ljust(linepos_width)}")
                file_line = lineno
            print('-' * len(header))
            for error in error_table:
                print(f"Error: {error}")
            total_line = file_line
            total_line -= 1

if __name__ == "__main__":
    lexer = Lexer()
    lexer.build()
    tables = lexer.test()
    lexer.pretty_print_testcases(tables)