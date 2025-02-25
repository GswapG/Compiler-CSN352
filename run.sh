
VERSION="1.2.82"

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

# Check if -h or --help is passed
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "Usage: run.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help      Show this help message and exit"
    echo "  -v, --version   Show version information and exit"
    echo "  -g, --graph     Render the graph for all testcases"
    exit 0
fi

# Check if -v or --version is passed
if [[ "$1" == "-v" || "$1" == "--version" ]]; then
    echo "parser.py version $VERSION"
    exit 0
fi

# Check if -g or --graph is passed
if [[ "$1" == "-g" || "$1" == "--graph" ]]; then
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

# Pass all arguments to the Python script
python3 src/parser.py "$@"
