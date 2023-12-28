from blessings import *
from colorama import Fore, Back, Style

term = Terminal()
print(term.clear(), end="")

msgs = ["hi", "hello", "welcome", "--- lol has joined ---", "lol said: lolll"]
p:int = 0

def print_msg(msg, p):
    if p == term.height - 3:
        with term.location(y=term.height - 1):
            print()
        print(term.move(p - 1, 0), term.clear_eol, end="")
        print(msg)
        return p
    print(term.move(p, 0), msg)
    return p + 1

def print_bar():
    print(term.move(term.height - 4, term.width), Fore.WHITE + Back.WHITE + " " * (term.width - 1))
    print(Style.RESET_ALL, term.clear_eol, end=" --> ")

for msg in msgs:
    p = print_msg(msg, p)

print_bar()

while True:
    msg = input()
    p = print_msg(msg, p)
    print_bar()