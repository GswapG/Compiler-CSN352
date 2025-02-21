# Compiler-CSN352

This is a compiler for a C-like language developed as a course project for CSN352: Compiler Design at IIT Roorkee.

## Overview

This project implements both a **Lexer** and a **Parser** for a C-like language. The lexer is built using `ply.lex` to tokenize source code, while the parser analyzes the syntax structure and generates a Syntax Tree .

## How to Run

### Lexer and Parser
1. Place your test cases in the 'testcases' folder as '.c' files
2. Run the following scripts in the project root:
     `run.sh` on Linux, `run.bat` on Windows
3. Use `-h` option for help
4. Use `-g` for Rendering the Parse Trees
5. Incase `run.sh` doesn't work run the following command : `chamod +x run.sh`

## Features

### Lexer Features
- **Tokenization of C-like Syntax**:
  - Identifies **keywords**, **identifiers**, **operators**, **literals**, and **punctuation**
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
  - Identifies illegal characters
  - Reports errors with line numbers and positions
- **String Literal Support**:
  - Handles Unicode-escaped strings and escape sequences

### Parser Features
- **Advanced C Language Constructs**:
  - **Control Structures**: if-else, for loop, while loop, do-while loop, switch cases
  - **Custom Control Flow**: until loop
  - **Jump Statements**: goto, break, continue
  - **Data Types**:
    - Basic types (int, float, double, char, _Bool, _Complex)
    - Multi-level pointers
    - Multi-dimensional arrays
    - Function pointers
  - **User-defined Types**:
    - Structs
    - Enums
    - Unions
  - **Storage Classes**:
    - static
    - extern
    - auto
    - register
    - const
    - volatile
  - **Memory Management**: Dynamic memory allocation
  - **I/O Operations**:
    - Command line input
    - File manipulation
    - printf and scanf functions
  - **Advanced Function Features**:
    - Recursive function calls
    - Function calls with arguments
    - Reference parameters
    - Typedef

### Visualization
- **Syntax Tree (Parse tree) Generation**:
  - Creates a visual representation of the program structure
  - Outputs an image file of the Parse tree in the `renderedTrees` directory

### Symbol Table Generation
- Produces a detailed symbol table showing:
  - Variable/function identifiers
  - Their corresponding types
  - Type information including qualifiers and storage classes

## Example Output

### Symbol Table Output
```
Parsing file: ./testcases\test4.c
+-------+----------------+
| Token | Type           |
+-------+----------------+
| f     | typedef int    |
| a     | f              |
| main  | PROCEDURE_int  |
+-------+----------------+
```
### Parse Tree Output

![Parse Tree Example](https://github.com/GswapG/Compiler-CSN352/blob/main/images/parseTree1.png)


### Lexical Analysis Output
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

## Project Structure
```
compiler-project/
├── main.py                      # Entry point
├── run.bat                      # Windows execution script
├── run.sh                       # Linux execution script
├── todo.md                      # Development tasks
├── C_grammar.md                 # Grammar specifications
├── README.md                    # This file
│
├── src/                         # Main source code
│   ├── lexer.py                 # Current lexical analyzer
│   ├── parser.py                # Syntax analyzer
│   ├── tokens.py                # Token definitions
│   ├── ply/                     # PLY library
│   └── renderedTrees/           # Generated Tree visualizations
│
├── old_lexer/                   # Previous lexer implementation
│   ├── lexer.py
│   ├── lexer_class.py
│   ├── defs/
│   ├── ply/
│   └── testcases/
│
├── renderedTrees/               # Generated parse tree outputs
│   ├── parseTree1.png
│   ├── parseTree2.png
│   └── ...
│
└── testcases/                   # Test C files
    ├── test1.c
    ├── test2.c
    └── ...
    └── output/                  # Compiled test outputs
```

## For Developers
Check the [TODO](todo.md) file for planned improvements and ongoing tasks.

## Technologies Used
- Python
- PLY (Python Lex-Yacc)
- Graphviz (for Tree visualization)

## Team Members
| S.No. | Name             | Enrollment No. |
| ----- | ---------------- | -------------- |
| 1.    | Garv Sethi       | 22115057       |
| 2.    | Granth Gaud      | 22114035       |
| 3.    | Swapnil Garg     | 22115150       |
| 4.    | Mmukul Khedekar  | 22114054       |
