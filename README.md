# Compiler-CSN352
This is a compiler for a C like language made as a course project for CSN352: Compiler Design course at IIT Roorkee.

# For devs - 
Read [TODO](todo.md)

## How to run 
### Lexer
1.  Put your testcases in 'testcases' folder as '.c' files.
2.  Run the following command in the project root-
```bash
python main.py
```
or run `run.sh` on Linux, `run.bat` on Windows.

## Overview
This project is a **Lexer for a C-like language**, built using `ply.lex`. It tokenizes source code, handling various language constructs such as keywords, operators, comments, and literals. The lexer supports multi-line comments, single-line comments, and error handling.

## Features
- **Tokenization of C-like Syntax**:
  - Identifies **keywords**, **identifiers**, **operators**, **literals**, and **punctuation**.
  - Supports:
    - **Bitwise Operators**: `&`, `|`, `^`, `~`, `<<`, `>>`
    - **Logical Operators**: `&&`, `||`, `!`
    - **Relational Operators**: `==`, `!=`, `>=`, `<=`, `>`, `<`
    - **Arithmetic Operators**: `+`, `-`, `*`, `/`, `%`, `++`, `--`
    - **Assignment Operators**: `=`, `+=`, `-=`, `*=`, `/=`, `%=`
    - **Ternary Operators**: `?`, `:`

- **Comment Handling**:
  - **Multi-line Comments**: `/* ... */`
  - **Single-line Comments**: `// ...`

- **Error Detection**:
  - Identifies illegal characters.
  - Reports errors with line numbers and positions.

- **String Literal Support**:
  - Handles Unicode-escaped strings and escape sequences.

- **Batch Processing of Test Files**:
  - Processes multiple `.c` files from the `testcases` directory.

- **Pretty-Printed Output**:
  - Displays tokens in a well-formatted table with:
    - **Lexeme**
    - **Token Type**
    - **Line Number**
    - **Line Position**

## Output Example
```
=======================  Test Case 1  =======================
Lexeme                        Token       Line No.   Line Pos.
--------------------------------------------------------------
int                           KEYWORD     1          0
main                          IDENTIFIER  1          4
(                             LPAREN      1          8
)                             RPAREN      1          9
{                             LBRACE      1          11
...                           ...         ...        ...
--------------------------------------------------------------
Error: Illegal character '@' at line 3, position 14
```

