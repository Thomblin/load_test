
from enum import Enum

class Color(Enum):
    RED = "\033[91m"
    GREEN = "\033[92m"
    END_COLOR = "\033[0m"

def __print_color(text: str, color: Color):
    print(f"{color.value}{text}{Color.END_COLOR.value}")

def print_error(text: str):
    __print_color(text, Color.RED)

def print_success(text: str):
    __print_color(text, Color.GREEN)

def print_info(text: str):
    print(text)