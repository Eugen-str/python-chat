import socket
import os
import time

IP = "192.168.1.117"
PORT = 5050
FORMAT = "utf-8"

if not IP:
    IP = input("Enter IP address: ")
if not PORT:
    PORT = input("Enter TCP port: ")

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect((IP, PORT))
        
def send_msg(msg):
    msg = msg.encode(FORMAT)
    client_sock.sendall(msg)

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

while True:
    os.system("cls" if os.name == 'nt' else "clear")
    msg = input_msg("Your message: ")
    send_msg(msg)

    if(msg == "!disc"):
        break

time.sleep(1)

client_sock.close()