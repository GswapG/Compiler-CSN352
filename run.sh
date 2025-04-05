#!/bin/bash
VERSION="1.3.198"
INTERPRETER="python3"

# Function to install Graphviz based on OS
install_graphviz() {
    echo "Graphviz is not installed. Installing now..."
    
    case "$(uname -s)" in
        Linux*)
            if command -v apt-get &>/dev/null; then
                echo "Detected Debian/Ubuntu system. Installing Graphviz using apt..."
                sudo apt-get install -y graphviz
            elif command -v yum &>/dev/null; then
                echo "Detected RHEL/CentOS system. Installing Graphviz using yum..."
                sudo yum install -y graphviz
            elif command -v pacman &>/dev/null; then
                echo "Detected Arch Linux system. Installing Graphviz using pacman..."
                sudo pacman -Sy --noconfirm graphviz
            else
                echo "Unsupported Linux distribution. Please install Graphviz manually."
                exit 1
            fi
            ;;
        Darwin*)
            echo "Detected macOS. Installing Graphviz using Homebrew..."
            if ! command -v brew &>/dev/null; then
                echo "Homebrew is not installed. Please install Homebrew first: https://brew.sh/"
                exit 1
            fi
            brew install graphviz
            ;;
        CYGWIN*|MINGW*|MSYS*)
            echo "Detected Windows. Installing Graphviz using Chocolatey..."
            if ! command -v choco &>/dev/null; then
                echo "Chocolatey is not installed. Please install it from https://chocolatey.org/install"
                exit 1
            fi
            choco install graphviz -y
            ;;
        *)
            echo "Unknown operating system. Please install Graphviz manually."
            exit 1
            ;;
    esac
}

# Parse arguments and detect --fast or --clear flag
ARGS=()
CLEAR=false
for arg in "$@"; do
    if [[ "$arg" == "--fast" ]]; then
        INTERPRETER="pypy3"
    elif [[ "$arg" == "-c" || "$arg" == "--clear" ]]; then
        CLEAR=true
    else
        ARGS+=("$arg")
    fi
done

# Check if -h or --help is passed
if [[ " ${ARGS[*]} " =~ " -h " || " ${ARGS[*]} " =~ " --help " ]]; then
    echo "Usage: run.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help      Show this help message and exit"
    echo "  -v, --version   Show version information and exit"
    echo "  -g, --graph     Render the graph for all testcases"
    echo "  --fast          Use PyPy3 instead of Python3"
    echo "  -c, --clear     Remove all files in output folder"
    exit 0
fi

# Check if -v or --version is passed
if [[ " ${ARGS[*]} " =~ " -v " || " ${ARGS[*]} " =~ " --version " ]]; then
    echo "Compiler version $VERSION"
    exit 0
fi

# Check if --clear flag is set
if [ "$CLEAR" = true ]; then
    if [ -d "renderedTrees" ]; then
        rm -rf renderedTrees/*
        echo "Cleared renderedTrees folder."
    fi
    if [ -d "renderedSymbolTables" ]; then
        rm -rf renderedSymbolTables/*
        echo "Cleared renderedSymbolTables folder."
    fi
    if [ -d "generatedIR" ]; then
        rm -rf generatedIR/*
        echo "Cleared generatedIR folder."
    fi
    if [ -d "renderedIRTrees" ]; then
        rm -rf rederedIRTrees/*
        echo "Cleared renderedIRTrees folder."
    fi
    exit 0
fi

# Check if -g or --graph is passed
if [[ " ${ARGS[*]} " =~ " -g " || " ${ARGS[*]} " =~ " --graph " ]]; then
    if ! command -v dot &> /dev/null; then
        echo "Graphviz is not installed."
        echo "To install Graphviz, run:"
        echo ""
        echo "  Ubuntu/Debian: sudo apt install graphviz"
        echo "  Mac (Homebrew): brew install graphviz"
        echo "  Windows (Chocolatey): choco install graphviz"
        echo ""

        install_graphviz
    fi
fi

# Run the script with the selected interpreter
$INTERPRETER main.py "${ARGS[@]}"
