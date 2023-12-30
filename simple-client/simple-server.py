import socket
import threading
import random

HEADER = 8
IP = socket.gethostbyname(socket.gethostname())
PORT = 5050
FORMAT = "utf-8"

RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
MAGENTA = '\033[35m'
CYAN = '\033[96m'
RESET = '\033[0m'

class ClientHandler:
    def __init__(self, conn, addr):
        self.nickname = ""
        self.conn: socket = conn
        self.addr = addr
        self.connected = True
        self.viewer = None
        self.token = 0
    
    def generate_token(self):
        self.token = random.randint(10000,99999)

    def set_nickname(self, nickname):
        self.nickname = nickname
    
    def send_msg(self, msg):
        try:
            if self.viewer:
                msg_len = len(bytes(msg.encode(FORMAT)))
                self.viewer.conn.sendall(str(msg_len).encode(FORMAT) + b' ' * (HEADER - len(str(msg_len))))
                msg = msg.encode(FORMAT)
                self.viewer.conn.sendall(msg)
            msg_len = len(bytes(msg.encode(FORMAT)))
            self.conn.sendall(str(msg_len).encode(FORMAT) + b' ' * (HEADER - len(str(msg_len))))
            msg = msg.encode(FORMAT)
            self.conn.sendall(msg)
            
            return 1
        except BrokenPipeError:
            print(RED + f"[ERROR] {self.nickname} has unsuccesfully disconnected, disconnecting again..." + RESET)
            self.connected = False
            self.conn.close()
            print(f"[CLIENT] Client {self.nickname} disconnected")

            return -1
    
    def recv_msg(self):
        msg_len = self.conn.recv(HEADER).decode(FORMAT)
        #print(f"[SERVER] Received msg_len = {msg_len}")
        if msg_len:
            msg = self.conn.recv(int(msg_len)).decode(FORMAT)
            return msg


class Server:
    def __init__(self):
        self.server_sock: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind((IP, PORT))
        
        self.clients: [ClientHandler] = []
    
    def run(self):
        print(GREEN + f"[SERVER] Starting server on address: {IP}" + RESET)

        self.server_sock.listen()
        print("[SERVER] Server listening")

        try:
            while True:
                conn, addr = self.server_sock.accept()
                client = ClientHandler(conn, addr)
                self.clients.append(client)
                
                thread = threading.Thread(target=self.handle_client, args=(client, ))
                thread.start()
        except KeyboardInterrupt:
            self.shut_down()
    
    def shut_down(self):
        if(self.clients != []):
            print("\n[SERVER] Server is not empty, disconnecting all connected clients")

            for c in self.clients:
                print(f"[SERVER] Closing : {c.nickname}")
                c.connected = False
                c.send_msg("!disc")
            
        print("\n[SERVER] Shutting server down...")
        self.server_sock.close()
        print(GREEN + "[SERVER] Server succesfully shut down" + RESET)
        exit(1)

    def handle_client(self, client: ClientHandler):
        nickname = client.recv_msg()
        
        if(nickname[0:6] == "!token"):
            token = nickname[7:15]
            for c in self.clients:
                if token == c.token:
                    c.viewer = client
                    client.set_nickname(c.nickname + "viewer")
                    client.token = token
        else:
            client.set_nickname(nickname)

            if client.nickname == "":
                import random
                client.set_nickname(str(random.randint(10000, 50000)))
                
            client.generate_token()
            print(CYAN + f"[CLIENT] Token of client {client.nickname}: {client.token}" + RESET)
            client.send_msg(YELLOW + f"Your token: {client.token}" + RESET)

        print(CYAN + f"[CLIENT] Client {client.nickname} connected" + RESET)
        self.broadcast(CYAN + f"--- User {client.nickname} has joined the chat! ---" + RESET)

        while client.connected:
            msg = client.recv_msg()
            print(f"{client.nickname} sent: {msg}")

            if msg == "!disc":
                print(CYAN + f"[CLIENT] Client {client.nickname} disconnected" + RESET)
                self.broadcast(CYAN + f"--- User {client.nickname} has disconnected from the chat ---" + RESET)
                client.connected = False
            
            elif msg == "!users":
                client.send_msg(YELLOW + "Online users: " + self.get_clients() + RESET)
            
            elif msg == "!help":
                help_str = CYAN + """Available commands:\n\t!users - show all connected users
                \t!nick - change nickname\n\t!help - show help text\n\t!disc - disconnect""" + RESET
                for c in self.clients:
                    if c.token == client.token:
                        c.send_msg(help_str)
            
            elif msg == "!nick":
                for c in self.clients:
                    if c.token == client.token:
                        c.send_msg(YELLOW + "- Set your new nickname: " + RESET)
                old = client.nickname
                client.set_nickname(client.recv_msg())
                print(CYAN + f"[CLIENT] Client {old} changed their username to {client.nickname}" + RESET)
                self.broadcast(CYAN + f"--- User {old} has changed their nickname to {client.nickname} ---" + RESET)

            elif msg == "!priv":
                for c in self.clients:
                    if c.token == client.token:
                        c.send_msg(help_str)
                client.send_msg(YELLOW + "Online users: " + self.get_clients())
                client.send_msg("- Send private message to: " + RESET)
                
                user = client.recv_msg()
                receiver = None

                for c in self.clients:
                    if c.nickname == user:
                        receiver = c
                
                if receiver == None:
                    client.send_msg(RED + "User not available" + RESET)
                elif receiver.nickname == client.nickname:
                    client.send_msg(RED + "Cannot send message to yourself" + RESET)
                else:
                    client.send_msg(YELLOW + "- Write private message: " + RESET)
                    priv_msg = client.recv_msg()
                    client.send_msg(YELLOW + "Message sent!" + RESET)
                    receiver.send_msg(YELLOW + f"- Private message from {client.nickname}:" + RESET + f"\n{priv_msg}")

            else:
                self.broadcast_msg(client, msg)
        
        client.conn.close()
        self.clients.remove(client)

    def broadcast_msg(self, sender, msg):
        self.clients.remove(sender)

        for client in self.clients:
            if client.send_msg(sender.nickname + ": " + msg) == -1:
                self.clients.remove(client)
        
        self.clients.append(sender)
    
    def broadcast(self, msg):
        for client in self.clients:
            client.send_msg(msg)
    
    def get_clients(self):
        clients_str = ""
        for c in self.clients:
            clients_str += "[" + c.nickname + "] "
        return clients_str

if __name__=="__main__":
    server = Server()
    server.run()
