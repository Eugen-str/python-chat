from asciimatics.screen import Screen
from asciimatics.event import KeyboardEvent

PROMPT = " => " 

p = 0
inp = []

def clear_line_at(screen, y, x=0):
    screen.print_at(" " * screen.width, x, y)

def clear_char(screen, x, y):
    screen.print_at(" ", x, y)

def input_msg(screen):
    global inp
    e = screen.get_event()
    if e and isinstance(e, KeyboardEvent):
        if e.key_code == ord('\n'):
            msg = ''.join(inp)
            inp = []
            clear_line_at(screen, screen.height - 1, len(PROMPT))
            return msg
        elif e.key_code == screen.KEY_BACK:
            if len(inp): 
                inp.pop()
            clear_char(screen, len(PROMPT) + len(inp), screen.height - 1)
        else:
            try:
                inp += chr(e.key_code)
            except:
                pass
    
    return ""

def print_bar(screen, y=0, char="─"):
    if not y: y = screen.height - 2
    screen.print_at(char * screen.width, 0, y)
    
def print_prompt(screen, y=0):
    if p + 3 > screen.height:
        screen.print_at(PROMPT + ''.join(inp), 0, p + 1)
    else:
        screen.print_at(PROMPT + ''.join(inp), 0, screen.height - 1)

def print_msg(msg, screen):
    global p

    if p + 3 > screen.height:
        clear_line_at(screen, p)
        screen.refresh()
        screen.scroll()
        print_bar(screen, p + 1)
        screen.print_at(msg, 0, p)
    else:
        screen.print_at(msg, 0, p)
    
    p += 1

def main(screen):
    print_bar(screen)
    while True:
        msg = input_msg(screen)
        print_prompt(screen)
        if len(msg):
            print_msg(msg, screen)
        screen.refresh()


Screen.wrapper(main)