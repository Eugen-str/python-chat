import socket
import os
import time

HEADER = 8
IP = "192.168.1.117"
PORT = 5050
FORMAT = "utf-8"

MSG_DISC = "!disc"

if not IP:
    IP = input("Enter IP address: ")
if not PORT:
    PORT = input("Enter TCP port: ")

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect((IP, PORT))
        
def send_msg(msg):
    msg_len = len(bytes(msg.encode(FORMAT)))
    client_sock.sendall(str(msg_len).encode(FORMAT) + b' ' * (HEADER - len(str(msg_len))))
    msg = msg.encode(FORMAT)
    client_sock.sendall(msg)

def receive_msg():
    msg_len = client_sock.recv(HEADER).decode(FORMAT)
    if msg_len:
        msg = client_sock.recv(int(msg_len)).decode(FORMAT)
        if msg == MSG_DISC:
            # not actually necessary to send "!disc", 
            # this is to stop the thread waiting for a message on shutdown
            send_msg("!disc")
        
        print(msg)

def input_msg(str=""):
    msg = ""
    while msg == "" or msg == "\n" or msg == "\r\n":
        try:
            msg = input(str)
        except KeyboardInterrupt:
            pass
    
    return msg

nickname = input_msg("Enter your nickname: ")
send_msg(nickname)

token = receive_msg()

while True:
    os.system("cls" if os.name == 'nt' else "clear")
    print("Your token: " + token)
    msg = input_msg("Your message: ")
    send_msg(msg)

    if(msg == "!disc"):
        break

time.sleep(1)

client_sock.close()