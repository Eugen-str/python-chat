import socket
import threading
import time

HEADER = 8
FORMAT = "utf-8"

IP = "192.168.1.117"
PORT = 5050

MSG_DISC = "!disc"

class Client:
    def __init__(self, ip_address, port):
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.connect((ip_address, port))
        self.connected = True

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
                
                print(msg)
                

    def run(self):
        thread = threading.Thread(target=self.receive_msg)
        thread.start()

        nickname = input_msg("Enter your nickname: ")
        
        self.send_msg(nickname)
        
        while self.connected:
            msg = input_msg()
            self.send_msg(msg)

            if(msg == "!disc"):
                break
        
        time.sleep(1)
        self.connected = False
        self.client_sock.close()

def input_msg(str=""):
    msg = ""
    while msg == "" or msg == "\n" or msg == "\r\n":
        try:
            msg = input(str)
        except KeyboardInterrupt:
            pass
    
    return msg

def main():
    print("Welcome to the chat!")
    print("For help use '!help', to connect to a server use '!conn'")
    while True:
        inp = input("--> ")
        
        if inp == "!exit":
            break
        elif inp == "!conn":
            ip = input("Enter the ip address: ")
            port = int(input("Enter TCP port: "))

            try:
                client = Client(IP, PORT)
                client.run()
            except:
                print("Unable to connect to server. Try again")
        elif inp == "!help":
            print("Available commands: ")
            print("\t!help - show this help screen")
            print("\t!conn - connect to local server")
            print("\t!exit - exit out of the program")
        else:
            print("Unknown command, use !help to show available options")


if __name__=="__main__":
    main()