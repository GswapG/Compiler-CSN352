@echo off
setlocal EnableDelayedExpansion
set VERSION=1.3.198
set INTERPRETER=python

:: Check if -h or --help is passed
if "%1" == "-h" goto help
if "%1" == "--help" goto help
if "%1" == "-v" goto version
if "%1" == "--version" goto version
if "%1" == "-c" goto clear
if "%1" == "--clear" goto clear

:: Check for --fast flag and remove it from arguments
set ARGS=
for %%A in (%*) do (
    if "%%A" == "--fast" (
        set INTERPRETER=pypy3
    ) else (
        set ARGS=!ARGS! %%A
    )
)

:: Run the script with the selected interpreter
%INTERPRETER% main.py !ARGS!
exit /b

:help
echo Usage: run.bat [OPTIONS]
echo.
echo Options:
echo   -h, --help      Show this help message and exit
echo   -v, --version   Show version information and exit
echo   -g, --graph     Render the graph for all testcases
echo   --fast          Use PyPy3 instead of Python
echo   -c, --clear     Remove all files in output folders
exit /b

:version
echo parser.py version %VERSION%
exit /b

:clear
if exist renderedTrees (
    del /q /f renderedTrees\*
    echo Cleared renderedTrees folder.
)
if exist renderedSymbolTables (
    del /q /f renderedSymbolTables\*
    echo Cleared renderedSymbolTables folder.
)
if exist generatedIR (
    del /q /f generatedIR\*
    echo Cleared generatedIR folder.
)
if exist renderedIRTrees (
    del /q /f renderedIRTrees\*
    echo Cleared renderedIRTrees folder.
)
exit /b
