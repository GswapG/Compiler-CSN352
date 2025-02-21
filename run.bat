@echo off
set VERSION=1.2.80

:: Check if -h or --help is passed
if "%1" == "-h" goto help
if "%1" == "--help" goto help
if "%1" == "-v" goto version
if "%1" == "--version" goto version

:: Pass all arguments to the Python script
python src\parser.py %*
exit /b

:help
echo Usage: run.bat [OPTIONS]
echo.
echo Options:
echo   -h, --help      Show this help message and exit
echo   -v, --version   Show version information and exit
echo   -g, --graph     Render the graph for all testcases
exit /b

:version
echo parser.py version %VERSION%
exit /b
