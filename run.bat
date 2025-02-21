@echo off
setlocal

set VERSION=1.2.65

:: Function to install Graphviz using Winget
:install_graphviz
echo Graphviz is not installed. Installing now...

:: Check if Winget is available
where winget >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Winget is not installed. Please install it from:
    echo https://learn.microsoft.com/en-us/windows/package-manager/winget/
    exit /b 1
)

echo Installing Graphviz using Winget...
winget install --id Graphviz.Graphviz -e --silent
exit /b 0

:: Show help message
:show_help
echo Usage: run.bat [OPTIONS]
echo.
echo Options:
echo   -h, --help      Show this help message and exit
echo   -v, --version   Show version information and exit
echo   -g, --graph     Render the graph for all testcases
exit /b 0

:: Show version
:show_version
echo parser.py version %VERSION%
exit /b 0

:: Check arguments
if "%~1"=="" goto :run_python

if "%~1"=="-h" goto :show_help
if "%~1"=="--help" goto :show_help

if "%~1"=="-v" goto :show_version
if "%~1"=="--version" goto :show_version

if "%~1"=="-g" goto :graph_check
if "%~1"=="--graph" goto :graph_check

goto :run_python

:: Check if Graphviz is installed
:graph_check
where dot >nul 2>nul
if %ERRORLEVEL% neq 0 (
    call :install_graphviz
)
goto :run_python

:: Run the Python script with all arguments
:run_python
python src/parser.py %*
exit /b 0
