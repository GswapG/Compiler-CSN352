import os
import re
import sys
import shutil
import tempfile

STANDARD_LIBS = {'stdio.h', 'stdlib.h', 'math.h', 'string.h', 'ctype.h'}

class Preprocessor:
    def __init__(self):
        self.macros = {}
        self.conditional_stack = []
        self.current_inclusion = True
        self.prototypes_written = False

    def process(self, input_path, output_file, current_dir=''):
        try:
            if not self.prototypes_written:
                prototypes = (
                    "void print_int(int x);\n"
                    "void print_float(float x);\n"
                    "void print_char(char x);\n"
                    "void print_string(const char *s);\n"
                    "void* malloc(int size);\n"
                    "void free(void* ptr);\n\n"
                )
                output_file.write(prototypes)
                self.prototypes_written = True

            with open(input_path, 'r') as f:
                for line_num, line in enumerate(f,start=1):
                    stripped = line.strip()
                    
                    # Process preprocessor directives.
                    if stripped.startswith('#'):
                        parts = re.split(r'\s+', stripped)
                        directive = parts[0].lower()
                        
                        if directive == '#ifdef':
                            self._handle_ifdef(parts)
                        elif directive == '#ifndef':
                            self._handle_ifndef(parts)
                        elif directive == '#endif':
                            self._handle_endif()
                        elif self.current_inclusion:
                            if directive == '#include':
                                self._handle_include((line,line_num), output_file, current_dir)
                            elif directive == '#define':
                                self._handle_define(parts)
                            elif directive == '#undef':
                                self._handle_undef(parts)
                            else:
                                raise Exception(f"Invalid preprocessor directive at line number {line_num}:\n{stripped}")
    
                    else:
                        if self.current_inclusion:
                            # Check if the line is a printf statement that needs to be expanded.
                            if stripped.startswith("printf"):
                                expanded = self._process_printf((line,line_num))
                                output_file.write(expanded + "\n")
                            else:
                                output_file.write(self._apply_macros(line))
        except IOError as e:
            raise Exception(f"Error processing {input_path}: {e}")

    def _handle_include(self, line, output, current_dir):
        line, line_num = line
        match = re.search(r'#include\s+[<"](.+?)[>"]', line)
        if not match:
            return
        
        filename = match.group(1)
        if '<' in line:
            if filename not in STANDARD_LIBS:
                raise ValueError(f"Unrecognized standard library at line {line_num}: {filename}")
        else:
            path = os.path.join(current_dir, filename)
            if not os.path.exists(path):
                raise FileNotFoundError(f"Missing file: {path}")
            parent_dir = os.path.dirname(path)
            self.process(path, output, parent_dir)

    def _handle_define(self, parts):
        if len(parts) < 2:
            return
        name = parts[1]
        value = ' '.join(parts[2:]) if len(parts) > 2 else ''
        self.macros[name] = value

    def _handle_undef(self, parts):
        if len(parts) >= 2 and parts[1] in self.macros:
            del self.macros[parts[1]]

    def _handle_ifdef(self, parts):
        if len(parts) < 2:
            self.current_inclusion = False
            return
        
        macro = parts[1]
        self.conditional_stack.append(self.current_inclusion)
        self.current_inclusion = self.current_inclusion and (macro in self.macros)

    def _handle_ifndef(self, parts):
        if len(parts) < 2:
            self.current_inclusion = False
            return
        
        macro = parts[1]
        self.conditional_stack.append(self.current_inclusion)
        self.current_inclusion = self.current_inclusion and (macro not in self.macros)

    def _handle_endif(self):
        if self.conditional_stack:
            self.current_inclusion = self.conditional_stack.pop()

    def _apply_macros(self, line):
        for macro in sorted(self.macros.keys(), key=len, reverse=True):
            line = re.sub(r'\b{}\b'.format(re.escape(macro)), self.macros[macro], line)
        # Remove the line if it becomes empty.
        if line.strip() == "":
            return ""
        return line

    def _process_printf(self, line):
        """
        Expands a printf statement into multiple print_* calls.
        For example:
            printf("Hi %d is an integer, %f is a float, %c is a char", x, y, z);
        is expanded into:
            print_string("Hi ");
            print_int(x);
            print_string(" is an integer, ");
            print_float(y);
            print_string(" is a float, ");
            print_char(z);
            print_string(" is a char");
        This function also adds error comments if an unknown conversion specifier is used
        or if the number of arguments doesn't match the number of conversion specifiers.
        """
        line, line_num = line
        # Pattern to extract the format string and the arguments.
        pattern = r'\s*printf\s*\(\s*"([^"]*)"\s*(?:,(.*))?\)\s*;'
        match = re.match(pattern, line)
        if not match:
            return line  # Return unchanged if not matching expected pattern.
        
        fmt = match.group(1)
        args_str = match.group(2)
        print(args_str)
        args = []
        if args_str:
            args = [arg.strip() for arg in args_str.split(',')]
        print(args)
        new_lines = []
        arg_index = 0

        # Use a generic pattern to capture any conversion specifier following '%'.
        specifier_pattern = re.compile(r'%(\S)')
        last_pos = 0
        percentage_exists = False
        for m in specifier_pattern.finditer(fmt):
            # Append any literal text before the specifier.
            literal = fmt[last_pos:m.start()]
            if literal:
                literal_escaped = literal.replace('"', r'\"')
                literal_escaped = literal_escaped.replace('%','')
                if percentage_exists:
                    literal_escaped = '%' + literal_escaped
                    percentage_exists = False
                new_lines.append(f'print_string("{literal_escaped}");')
            
            spec = m.group(1)
            # Only allow %d, %f, %c.
            if spec not in ['d', 'f', 'c','s','%', ' ']:
                raise Exception(f"Unknown conversion identifier at line {line_num}: {spec}")
            else:
                if arg_index < len(args):
                    if spec == 'd':
                        print(args[arg_index])
                        new_lines.append(f'print_int({args[arg_index]});')
                    elif spec == 'f':
                        new_lines.append(f'print_float({args[arg_index]});')
                    elif spec == 'c':
                        new_lines.append(f'print_char({args[arg_index]});')
                    elif spec == 's':
                        new_lines.append(f"print_string({args[arg_index]});")
                    elif spec == '%':
                        arg_index -= 1
                        percentage_exists = True
                    arg_index += 1
                else:
                    raise Exception(f"Missing argument at line {line_num} for : {spec}")
            last_pos = m.end()
        # Append any trailing literal text after the last specifier.
        trailing_literal = fmt[last_pos:]
        if trailing_literal:
            if percentage_exists:
                trailing_literal = '%' + trailing_literal
                percentage_exists = False
            trailing_literal = trailing_literal.replace('"', r'\"')
            new_lines.append(f'print_string("{trailing_literal}");')
        
        # Check if there are extra arguments that weren't used.
        if arg_index < len(args):
            raise Exception(f"Provided too many arguments for printf at line {line_num}")
        return " ".join(new_lines)

def preprocess(input_file, output_file):
    processor = Preprocessor()
    with open(output_file, 'w') as out:
        processor.process(input_file, out, os.path.dirname(input_file))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: c_preprocessor.py input.c output.c")
        sys.exit(1)

    input_path = os.path.abspath(sys.argv[1])
    output_path = os.path.abspath(sys.argv[2])

    if input_path == output_path:
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(
                mode='w',
                dir=os.path.dirname(input_path),
                delete=False,
                suffix='.c'
            ) as tmp:
                temp_file = tmp.name
            
            preprocess(input_path, temp_file)
            
            shutil.move(temp_file, input_path)
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
            sys.exit(1)
        finally:
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
    else:
        preprocess(input_path, output_path)
