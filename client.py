import socket
import threading

IP = "192.168.1.117"
PORT = 5050
FORMAT = "utf-8"

MSG_DISC = "!disc"

class Client:
    def __init__(self, ip_address, port):
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

if not IP:
    IP = input("Enter IP address: ")
if not PORT:
    PORT = input("Enter TCP port: ")

client = Client(IP, PORT)
client.run()