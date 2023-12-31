import socket
import threading
import time
from asciimatics.screen import Screen
from asciimatics.event import KeyboardEvent

HEADER = 8
FORMAT = "utf-8"

IP = "192.168.1.117"
PORT = 5050

PROMPT = " => " 

MSG_DISC = "!disc"

p = 0
inp = []

class Client:
    def __init__(self, ip_address, port, nickname, screen):
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.connect((ip_address, port))
        self.connected = True
        self.nickname = nickname
        self.screen = screen

    def send_msg(self, msg):
        msg_len = len(bytes(msg.encode(FORMAT)))
        self.client_sock.sendall(str(msg_len).encode(FORMAT) + b' ' * (HEADER - len(str(msg_len))))
        msg = msg.encode(FORMAT)
        self.client_sock.sendall(msg)

    def receive_msg(self):
        while self.connected:
            msg_len = self.client_sock.recv(HEADER).decode(FORMAT)
            if msg_len:
                msg = self.client_sock.recv(int(msg_len)).decode(FORMAT)
                if msg == MSG_DISC:
                    # not actually necessary to send "!disc", 
                    # this is to stop the thread waiting for a message on shutdown
                    self.send_msg("!disc")
                    self.connected = False
                    break
                
                print_msg(msg, self.screen)

    def run(self):
        thread = threading.Thread(target=self.receive_msg)
        thread.start()

        self.send_msg(self.nickname)
        
        while self.connected:
            msg = input_msg(self.screen)
            
            print_prompt(self.screen)
            
            if msg:
                self.send_msg(msg)
                print_msg(msg, self.screen)
            
                if(msg == "!disc"):
                    break
            
            self.screen.refresh()
        
        time.sleep(0.3)
        self.connected = False
        self.client_sock.close()


### Graphics

def clear_screen(screen):
    global p
    p = 0
    screen.clear_buffer(screen.COLOUR_WHITE, screen.A_NORMAL, screen.COLOUR_DEFAULT)
    print_bar(screen)
    print_prompt(screen)

def clear_line_at(screen, y, x=0):
    screen.print_at(" " * screen.width, x, y, bg=screen.COLOUR_DEFAULT)

def clear_char(screen, x, y):
    screen.print_at(" ", x, y, bg=screen.COLOUR_DEFAULT)

def input_msg(screen):
    global inp

    e = screen.get_event()
    if e and isinstance(e, KeyboardEvent):
        if e.key_code == ord('\n') or e.key_code == 13:
            msg = ''.join(inp)
            inp = []
            clear_line_at(screen, screen.height - 1, len(PROMPT))
            return msg
        elif e.key_code == screen.KEY_BACK:
            if len(inp): 
                inp.pop()
            clear_char(screen, len(PROMPT) + len(inp), screen.height - 1)
            clear_char(screen, len(PROMPT) + len(inp) + 1, screen.height - 1)
        else:
            try:
                inp += chr(e.key_code)
            except:
                pass
    
    return None

def print_bar(screen, y=0, char="─"):
    if not y: y = screen.height - 2
    screen.print_at(char * screen.width, 0, y, bg=screen.COLOUR_DEFAULT)
    
def print_prompt(screen, y=0):
    global p
    
    if p + 3 > screen.height:
        screen.print_at(PROMPT + ''.join(inp) + "█", 0, p + 1, bg=screen.COLOUR_DEFAULT)
    else:
        screen.print_at(PROMPT + ''.join(inp) + "█", 0, screen.height - 1, bg=screen.COLOUR_DEFAULT)

def print_msg(msg, screen):
    global p

    if p + 3 > screen.height:
        clear_line_at(screen, p)
        screen.refresh()
        screen.scroll()
        print_bar(screen, p + 1)
        screen.print_at(msg, 0, p, bg=screen.COLOUR_DEFAULT)
    else:
        screen.print_at(msg, 0, p, bg=screen.COLOUR_DEFAULT)
    
    p += 1


INCORRECT_MSG = "Incorrect usage of command. Type !help for help"

def cmd_help(screen):
    print_msg("These are the available commands: ", screen)
    print_msg("    !conn <ip> <port> - connect to server", screen)
    print_msg("    !nick <nickname> - set nickname", screen)
    print_msg("    !help - show this help screen", screen)
    print_msg("    !disc - disconnect from server", screen)
    print_msg("    !exit - exit the program\n", screen)

def cmd_conn(screen, nickname, prompt):
    global p
    if not nickname:
        print_msg("Set your nickname before joining a server with !nick", screen)
        
    elif not len(prompt) == 3:
        print_msg(INCORRECT_MSG, screen)
    
    else:
        ip = prompt[1]
        port = int(prompt[2])
        
        try:
            client = Client(ip, port, nickname, screen)
            
            clear_screen(screen)

            client.run()
           
        except Exception as e:
            print_msg(f"ERROR: {e}", screen)
            print_msg("Something went wrong. Try again\n", screen)


def cmd_nick(screen, prompt):
    if len(prompt) == 2:
        print_msg(f"Nickname changed to: '{prompt[1]}'", screen)
        return prompt[1]
    else:
        print_msg(INCORRECT_MSG, screen)
        return None

def main(screen):
    global p
    nickname = None
    clear_screen(screen)
    should_exit = False
    print_msg("Welcome to the chat!", screen)
    print_msg("type !help to see the available commands", screen)
    
    print_bar(screen)
    while not should_exit:
        prompt = input_msg(screen)
        print_prompt(screen)

        if prompt:
            prompt = prompt.split(' ')
            cmd = prompt[0]
            
            if cmd == "!help":
                cmd_help(screen)
            
            elif cmd == "!conn":
                cmd_conn(screen, nickname, prompt)

            elif cmd == "!nick":
                nickname = cmd_nick(screen, prompt)

            elif cmd == "!exit":
                should_exit = True
            
            else:
                print_msg("type !help to see the available commands", screen)

        screen.refresh()


Screen.wrapper(main)