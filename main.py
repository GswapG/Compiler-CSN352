from src.lexer_class import *

if __name__ == '__main__':
    lexer = Lexer()
    lexer.build()
    output = lexer.test()   
    lexer.pretty_print_testcases(output)