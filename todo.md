# General
1. run main.py from project root to run lexer
2. dont worry if imports dont work in files inside src (python module imports work this way)
3. lexer.py is outdated, and has been refactored into lexer_class.
4. Any changes to lexer need to be made to lexer_class


# TODO
- [x] character matching - add support for escape sequences.
- [ ] 'abcd' is matched as abcd-identifier, find a fix or delay to parsing
- [ ] 123abc is split as 123-int and abc-identifier, parit says parsing me fix hoga
- [ ] Add testcases to cover all types of tokens and situation exhaustively
- [x] Write a 'run' script for both windows and linux
