# Compiler-CSN352: A Comprehensive C-like Language Compiler

## Project Overview

This compiler project implements a full-featured compiler for a C-like language, developed as a course project for CSN352: Compiler Design at IIT Roorkee. The compiler provides a comprehensive approach to source code processing through multiple compilation stages.

## Compilation Stages

### 1. Preprocessor Stage (cpp.py)

**Output**: Pre-Processed Code

- Macro Preprocessing Support
  - Object-like macros
  - Function-like macros
  - Macro expansion
  - Conditional compilation directives (`#ifdef`, `#ifndef`, `#define`, `#undef`)
- Standard library file reference validation
- Directive parsing and preprocessing
- Preliminary error detection
- Note: No full linking implemented at this stage

**Output Example:**

> ```
> Preprocessed: ff84274d-67f4-42f7-bd98-394db3e29328.c
> ╔══════════ File Contents ══════════╗
> ║ void print_int(int x);            ║
> ║ void print_float(float x);        ║
> ║ void print_char(char x);          ║
> ║ void print_string(const char *s); ║
> ║                                   ║
> ║ enum Color {TRUE, FALSE};         ║
> ║ int main() {                      ║
> ║     int* x;                       ║
> ║     int y = *x;                   ║
> ║ }                                 ║
> ╚═══════════════════════════════════╝
> Parsing file: C:\Users\mailg\AppData\Local\Temp\tmpaic2idcm.c
> ```

### 2. Lexical Analysis Stage
**Output**: Token Stream
- Tokenizes source code into meaningful components
- Supports complex lexical features:
  - Bitwise, Logical, Relational Operators
  - Arithmetic and Assignment Operators
  - Comment Handling (Multi-line and Single-line)
  - Error Detection with Line and Position Reporting

### 3. Syntax Analysis Stage
**Output**: Parse Tree
- Generates a visual Syntax Tree
- Validates program structure
- Supports advanced C language constructs

**Parse Tree Example:**
![Parse Tree](images/parseTree1.png)

### 4. Semantic Analysis Stage
**Output**: 
- Scope Tree
- Symbol Table with Detailed Information

**Advanced Semantic Analysis Features:**
- Type Checking and Validation
  - Strict type compatibility checks
- Scope Management
  - Nested scope handling
  - Block-level scope tracking
- Advanced Type Support
  - Structs with nested fields
  - Unions with type-punning support
  - Enum type validation
- Function Semantics
  - Recursive function detection and validation
  - Variable argument function support (ellipsis)
  - Function pointer semantics
- Memory and Pointer Semantics
  - Pointer arithmetic validation
  - Multi-level pointer type checking
  - Dynamic memory allocation semantic checks
- Advanced Language Constructs
  - Static variable semantics
  - Const qualifier handling
  - Typedef semantic validation
  - Command Line Input

**Symbol Table Example:**
```
+--------------+-------------+-----------+---------+-------------+--------+----------+
| Name         | Type        | Kind      |   Scope | ScopeName   |   Size |   Offset |
+==============+=============+===========+=========+=============+========+==========+
| fun          | int         | function  |       0 | global      |      0 |        0 |
+--------------+-------------+-----------+---------+-------------+--------+----------+
| i            | int         | parameter |       1 | block@1     |      4 |        0 |
+--------------+-------------+-----------+---------+-------------+--------+----------+
| _VAR_ARGS_   | ...         | parameter |       1 | block@1     |        |        0 |
+--------------+-------------+-----------+---------+-------------+--------+----------+
| main         | int         | function  |       0 | global      |      0 |        0 |
+--------------+-------------+-----------+---------+-------------+--------+----------+
| a            | int         | variable  |       1 | block@1     |      4 |        0 |
+--------------+-------------+-----------+---------+-------------+--------+----------+
| x            | *int        | variable  |       1 | block@1     |      8 |        4 |
+--------------+-------------+-----------+---------+-------------+--------+----------+
| z            | int         | variable  |       1 | block@1     |      4 |       12 |
+--------------+-------------+-----------+---------+-------------+--------+----------+
```
**Scope Tree Example:**

![Scope Tree](images/scopes.c.png)


### 5. IR Generation (3AC)

**Output of IR Stage**: 
- Three Address Code Intermediate Representation
- Visual Representation in form of IR-Tree to understand the data flow of code generation

**Advanced Supported Features**
- Implicit and Explicit Type Conversion
- Variable Arguments
- Multidimensional array access and declaration
- Multilevel pointer and dereferencing
- Struct/Union Access using DOT and -> operators
- Enumerators
- typedef
- Operators with types
- Recursion
- CLI
- Until Loops

**Example Output**

```assembly
.fun:
    BeginFunc
    return 11
    EndFunc

.main:
    BeginFunc
    a = 11
    @t0 = & a
    x = @t0
    @t1 = charToint 'a'
    z = @t1
    param z
    param a
    @t2 = call fun, 2
    EndFunc
```

## Quick Start

### Prerequisites
- Python 3.9+
- Install dependencies: `pip install -r requirements.txt`
- Optional: PyPy3 for JIT compilation

### Running the Compiler

#### Preparing Execution Scripts
If `run.sh` doesn't have execute permissions:
```bash
# Make the script executable
chmod +x run.sh

# Alternative for specific file
chmod u+x run.sh   # Give user execute permission
chmod a+x run.sh   # Give all users execute permission
```

#### Standard Execution
```bash
# Linux
./run.sh 

# Windows
run.bat
```

#### Fast Compilation (JIT)
```bash
# Requires PyPy3 installed
./run.sh --fast
```

### Command Line Options
- `-h`: Help
- `-g`: Render Parse Trees
- `--fast`: Enable JIT Compilation
- `-d` to choose an entire directory of test cases to run the compiler
- `--no-ir` to disable IR Generation

## Project Structure
```
compiler-project/
├── main.py                  # Entry point
├── src/                     # Source code
│   ├── cpp.py               # Preprocessor
│   ├── lexer.py             # Lexical Analyzer
│   ├── parser.py            # Syntax Analyzer
│   ├── symtab.py            # Symbol Table Generator
│   └── ...
├── testcases/               # Test C files
├── tests/                   # Comprehensive Test Suites
│   ├── small/               # Small test cases
│   └── large/               # Large test cases
└── renderedTrees/           # Generated parse trees
```

## Technologies
- Python
- PLY (Python Lex-Yacc)
- Graphviz
- Rich (For Pretty Tables)
- CryptoHash (Used to generate hashes for stress testing)
- Optional: PyPy3 for JIT (Useful for large or many files)

## Known Issues and Contributions

### Semantic Bugs
- Detailed semantic bugs are tracked in `todo.md`
- Community contributions welcome!

### How to Contribute
1. Check `todo.md` for known issues
2. Raise issues on the GitHub repository
3. Submit pull requests with fixes or improvements

## Team Members
| Name           | Enrollment No. |
| -------------- | -------------- |
| Garv Sethi     | 22115057       |
| Granth Gaud    | 22114035       |
| Swapnil Garg   | 22115150       |
| Mmukul Khedekar| 22114054       |
