import socket
import threading

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

INCORRECT_MSG = "Incorrect usage of command. Type !help for help"

class ClientHandler:
    def __init__(self, conn, addr):
        self.conn: socket = conn
        self.addr = addr
        self.connected = True
    
    def set_nickname(self, nickname):
        self.nickname = nickname
    
    def send_msg(self, msg):
        try:
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
        client.set_nickname(client.recv_msg())

        if client.nickname == "":
            import random
            client.set_nickname(str(random.randint(10000, 50000)))
        
        print(CYAN + f"[CLIENT] Client {client.nickname} connected" + RESET)
        self.broadcast(f"--- User {client.nickname} has joined the chat! ---")

        while client.connected:
            msg = client.recv_msg()
            print(f"{client.nickname} sent: {msg}")

            prompt = msg.split(' ')
            cmd = prompt[0]

            if cmd == "!disc":
                print(CYAN + f"[CLIENT] Client {client.nickname} disconnected" + RESET)
                self.broadcast(f"--- User {client.nickname} has disconnected from the chat ---")
                client.connected = False

            elif cmd == "!users":
                client.send_msg("Online users: " + self.get_clients())
            
            elif cmd == "!help":
                help_str = CYAN + """Available commands:\n\t!users - show all connected users
                \t!nick <nickname> - change nickname\n\t!priv <user> <msg> - send private message to user
                \t!help - show help text\n\t!disc - disconnect""" + RESET
                client.send_msg(help_str)
            
            elif cmd == "!nick":
                if len(prompt) == 2:
                    old = client.nickname
                    client.set_nickname(prompt[1])
                    print(CYAN + f"[CLIENT] Client {old} changed their username to {client.nickname}" + RESET)
                    self.broadcast(f"--- User {old} has changed their nickname to {client.nickname} ---")
                else:
                    client.send_msg(INCORRECT_MSG)


            elif cmd == "!priv":
                if len(prompt) == 3 and prompt[1] != '' and prompt[2] != '':
                    user = prompt[1]
                    for c in self.clients:
                        if c.nickname == user:
                            c.send_msg(f"Private message from {client.nickname}")
                            c.send_msg(f"{client.nickname}: {prompt[2]}")
                            continue
                
                client.send_msg(INCORRECT_MSG)

            elif cmd == "!conn":
                client.send_msg("You are already connected! To connect to a different server, disconnect first")
            
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
