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

    def process(self, input_path, output_file, current_dir=''):
        try:
            with open(input_path, 'r') as f:
                for line in f:
                    stripped = line.strip()
                    
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
                                self._handle_include(line, output_file, current_dir)
                            elif directive == '#define':
                                self._handle_define(parts)
                            elif directive == '#undef':
                                self._handle_undef(parts)
                            else:
                                raise Exception(f"Invalid preprocessor directive :\n{stripped}")
    
                    else:
                        if self.current_inclusion:
                            output_file.write(self._apply_macros(line))
        except IOError as e:
            raise Exception(f"Error processing {input_path}: {e}")

    def _handle_include(self, line, output, current_dir):
        match = re.search(r'#include\s+[<"](.+?)[>"]', line)
        if not match:
            return
        
        filename = match.group(1)
        if '<' in line:
            if filename not in STANDARD_LIBS:
                raise ValueError(f"Unrecognized standard library: {filename}")
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
        empty = True
        for c in line:
            if not c.isspace():
                empty = False
                break
        if empty:
            line = ""
        return line

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