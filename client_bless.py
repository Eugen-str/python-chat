import socket
import threading
from getch import getch
from blessings import *
from colorama import Fore, Back, Style

IP = "192.168.1.117"
PORT = 5050
FORMAT = "utf-8"

MSG_DISC = "!disc"

class TermThreadHandling:
    def __init__(self):
        self.term = Terminal()
        self.msg_p = 0
        self.input_p = 0

        self.input_msg = " --> "
        self.input_y = self.height() - 2
        self.input_x = len(self.input_msg)
    
    def to_next_msg(self):
        print(self.term.move(self.msg_p, 0) + "")

    def print_msg(self, msg):
        """if self.p == self.term.height - 3:
            with self.term.location(y=self.term.height - 1):
                print()
            print(self.term.move(self.p - 1, 0), self.term.clear_eol, end="")
            print(msg)
            return"""
        
        self.to_next_msg()
        print(msg)
        self.msg_p += 1

        self.to_input()

    def print_bar(self, inp=""):
        print(self.term.move(self.height() - 4, self.width()) + Fore.WHITE + Back.WHITE + " " * (self.term.width - 1))
        print(Style.RESET_ALL, self.term.clear_eol, end=self.input_msg)
        print(inp, end="")

    def to_input(self):
        print(self.term.move(self.input_y, self.current_input_position_x()) + "", end="")

    def input_new_char(self):
        self.input_p += 1

    def input_remove_char(self):
        if self.input_p > 0:
            self.input_p -= 1

    def input_reset(self):
        self.input_p = 0

    def height(self):
        return self.term.height
    
    def width(self):
        return self.term.width

    def current_input_position_x(self):
        return self.input_p + self.input_x


class Client:
    def __init__(self):
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.term_handler = TermThreadHandling()

    def connect(self, ip_address, port):
        #TODO: try-except
        self.client_sock.connect((ip_address, port))
        self.connected = True

    def send_msg(self, msg):
        msg = msg.encode(FORMAT)
        self.client_sock.sendall(msg)

    def receive_msg(self):
        while self.connected:
            msg = self.client_sock.recv(1024).decode(FORMAT)
            if msg == MSG_DISC:
                # not actually necessary to send "!disc", 
                # this is to stop the thread waiting for a message on shutdown
                self.send_msg("!disc")
                self.connected = False
                break
            if msg:
                self.term_handler.print_msg(msg)

    def run(self):
        print(self.term_handler.term.clear(), end="")
        thread = threading.Thread(target=self.receive_msg)
        thread.start()

        self.term_handler.print_msg("Enter your nickname")
        self.term_handler.print_bar()
        nickname = self.input_msg()
        self.term_handler.print_msg(f"Nickname set to {nickname}")

        self.send_msg(nickname)
        
        while self.connected:
            self.term_handler.print_bar()
            msg = self.input_msg()
            self.term_handler.print_msg("you: " + msg)
            self.send_msg(msg)

            if(msg == "!disc"):
                break

        self.connected = False
        self.client_sock.close()

    def input_msg(self):
        msg = []
        while True:
            try:
                self.term_handler.print_bar(''.join(msg))
                char = getch()
                if char == '\n':
                    break
                elif char == '\x7f':
                    if msg:
                        msg.pop()
                        self.term_handler.input_remove_char()
                else:
                    msg.append(char)
                    self.term_handler.input_new_char()
                self.term_handler.print_bar(''.join(msg))
            except KeyboardInterrupt:
                pass
        
        return ''.join(msg)

client = Client()
client.connect(IP, PORT)
client.run()