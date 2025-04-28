#!/bin/bash
# filepath: d:\DevProjects\Compiler-CSN352\generatedASM\test.sh

# Directory containing the assembly files
ASM_DIR="./generatedASM"

# Output directory for object files
OBJ_DIR="./generatedASM/obj"
mkdir -p "$OBJ_DIR"

# Output directory for executables
BIN_DIR="./generatedASM/bin"
mkdir -p "$BIN_DIR"

# Check if nasm and ld are installed
if ! command -v nasm &>/dev/null; then
    echo "Error: nasm is not installed. Please install it to proceed."
    exit 1
fi

if ! command -v ld &>/dev/null; then
    echo "Error: ld is not installed. Please install it to proceed."
    exit 1
fi

# Iterate over all .asm files in the generatedASM directory
for asm_file in "$ASM_DIR"/*.asm; do
    # Extract the base filename without extension
    base_name=$(basename "$asm_file" .asm)

    # Compile the assembly file into an object file
    obj_file="$OBJ_DIR/$base_name.o"
    nasm -f elf64 "$asm_file" -o "$obj_file"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to assemble $asm_file"
        continue
    fi

    # Link the object file into an executable
    bin_file="$BIN_DIR/$base_name"
    ld -o "$bin_file" "$obj_file" -lc --dynamic-linker /lib64/ld-linux-x86-64.so.2
    if [ $? -ne 0 ]; then
        echo "Error: Failed to link $obj_file"
        continue
    fi

    echo "Successfully built $bin_file"
done

# Run all executables
for bin_file in "$BIN_DIR"/*; do
    echo "Running $bin_file..."
    "$bin_file"
    echo "-----------------------------------"
done
