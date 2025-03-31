from src.parser import *
from src.cpp import *

import os
import sys
import tempfile
import pickle
from Crypto.Hash import SHA256
import uuid

HASH_FILE = "hashes.bin"
STRESS_TESTING = './stress_testing'
DEFAULT_SOURCE_DIR = './tests/testing'
TREE_PATH = './renderedTrees'
SYMBOL_TABLE_PATH = './renderedSymbolTables'

# Command line arguments
strargv = [str(x) for x in sys.argv]

# Hashes
hashes = []

# Testcase directory/file
testcase_dir = DEFAULT_SOURCE_DIR
if "-d" in strargv or "--directory" in strargv:
    position = 1 + (strargv.index("-d") if strargv.index("-d") != -1 else strargv.index("--directory"))
    if len(strargv) <= position:
        raise Exception("Incorrect use of the flag \"-d\" or \"--directory\". Please specify the directory path following the flag.")
    testcase_dir = strargv[position]
    print(testcase_dir)

specific_filename = None
if "-f" in strargv or "--file" in strargv:
    position = 1 + (strargv.index("-f") if strargv.index("-f") != -1 else strargv.index("--file"))
    if len(strargv) <= position:
        raise Exception("Incorrect use of the flag \"-f\" or \"--file\". Please specify the directory path following the flag.")
    
    specific_filename = strargv[position]

graphgen = False
if "-g" in strargv or "--graph" in strargv:
    graphgen = True

irgen = True
if "--no-ir" in strargv:
    irgen = False

# Utils
def strip_file(file):
    lines = file.split('\n')
    new_file = ""
    for line in lines:
        new_file += line.strip()
    return new_file

def hash(input_file):
    input_file = strip_file(input_file)
    h = SHA256.new()
    h.update(input_file.encode())
    return h.hexdigest()

def calc_and_dump_hashes():
    for filename in os.listdir(STRESS_TESTING):
        if not (filename.endswith(".c") or filename.endswith(".C")):
            continue
        filepath = os.path.join(STRESS_TESTING, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r') as file:
                data = file.read()
            hashes.append(hash(data))

def add_file(filepath):
    with open(filepath, "r") as f:
        file = f.read()
    h = hash(file)
    if h in hashes:
        return
    hashes.append(h)
    filename = str(uuid.uuid4()) + '.c'
    filepath = os.path.join(STRESS_TESTING, filename)
    with open(filepath, "w") as f:
        f.write(file)
        f.close()

def process_file(filename,source_dir=testcase_dir):
    if not (filename.endswith('.c') or filename.endswith('.C')):
        return
    input_path = os.path.join(source_dir, filename)
    # Create a temporary file for the preprocessed output.
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.c') as temp_file:
        preprocess(input_path, temp_file.name)
        pretty_print_header(f"Compilation Results for: {filename}", text_style="bold underline red", border_style="green")
        print(f"Preprocessed: {filename} -> {temp_file.name}")

    # Pass the temporary file to the parser.
    parseFile(temp_file.name,filename,TREE_PATH,SYMBOL_TABLE_PATH,graphgen,irgen)

    add_file(input_path)
    return temp_file.name
    
def process_directory(source_dir=testcase_dir):
    """
    For all .c files in source_dir, run preprocessor on them to create a temp file and pass it onto the parser.
    """
    # Check if specific file is to be parsed
    calc_and_dump_hashes()
    if specific_filename is not None:
        if not os.path.exists(specific_filename):
            raise Exception(f"Error: {specific_filename} does not exist. Make sure the path is correct!!")
        directory, filename = os.path.split(specific_filename)
        process_file(filename,directory)
        return
    if not os.path.isdir(source_dir):
        raise Exception(f"Error: {source_dir} is not a valid directory.")
    temp_files = []
    for filename in os.listdir(source_dir):
        ret = process_file(filename)
        temp_files.append(ret)

    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    with open(HASH_FILE, 'wb') as file:
        pickle.dump(hashes, file)

if __name__ == "__main__":
    process_directory()