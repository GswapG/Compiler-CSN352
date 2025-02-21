#!/bin/bash

VERSION="1.2.65"

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

if [[ "$1" == "-v" || "$1" == "--version" ]]; then
    echo "parser.py version $VERSION"
    exit 0
fi

# Pass all arguments to the Python script
python3 src/parser.py "$@"