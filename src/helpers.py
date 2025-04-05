from rich.box import DOUBLE
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
import fnmatch
import re

console = Console()

def pretty_type_concat(*args):
    return_type = ""
    for arg in args:
        if arg is not None and arg != "":
            if len(return_type) > 0:
                if return_type[-1] == " ":
                    return_type += arg
                else:
                    if arg.startswith("*"):
                        return_type += arg 
                    else:
                        return_type += " " + arg
            else:
                return_type += arg
    ptr_count = return_type.count("*")
    if return_type.endswith("*" * ptr_count):
        if ptr_count == 0:
            return return_type
        new_type = "*" * ptr_count + return_type[:-ptr_count]
        return new_type

    else:
        raise Exception(f"wrong pretty_type for {args} parsed as {return_type}")
    
    pass

def pretty_print_header(header, text_style = "white", border_style = "white"):
    header = Panel(Text(header, style=text_style), border_style = border_style, expand = False)
    console.print(header)

def pretty_print_box(data, title):
    console.print(Panel(data, title=title, box=DOUBLE, expand=False))


def pretty_print_test_output(data , color): 
    console.print(Panel(data, style=color, expand=False))

def spaced(word):
    new_word = ""
    for i in range(len(word)):
        if len(new_word) == 0:
            if word[i] != ' ':
                new_word += word[i]
        else:
            if word[i] == ' ':
                if new_word[-1] != ' ':
                    new_word += word[i]
            else:
                new_word += word[i]
    return new_word

def trim_value(type, value):
    """
    trim out value qualifiers from a type in the middle
    """
    if isinstance(type, str):
        # if type starts with value, just strip the beginning
        if type.startswith(f"{value} "):
            type_without_value = type[len(f"{value} "):]
            return spaced(type_without_value)
        
        # if variable type is value char** c
        # then symbol table entry type is "**value char"
        # in that case, i'll strip all the beginning ** and then strip value if it exists
        # and then return **char (for example)
        elif f"{value} " in type:
            type_without_value = type.replace(f"{value} ", "", 1)
            return spaced(type_without_value)

    return type

def strip_value(type, value):
    """
    strip out value qualifiers from a type from the beginning
    """

    if isinstance(type, str):
        # if type starts with value, just strip the beginning
        if type.startswith(f"{value} "):
            type_without_value = type[len(f"{value} "):]
            return type_without_value
        
    return type