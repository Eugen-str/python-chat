import socket
import threading

IP = socket.gethostbyname(socket.gethostname())
PORT = 5050
SERVER = (IP, PORT)
FORMAT = "utf-8"

class ClientHandler:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.connected = True
    
    def set_nickname(self, nickname):
        self.nickname = nickname
    
    def send_msg(self, msg):
        try:
            self.conn.send(msg.encode(FORMAT))
        except BrokenPipeError:
            print(f"[ERROR] {self.nickname} has disconnected, but server has attempted to send data to them")

class Server:
    def __init__(self):
        self.server_sock: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind(SERVER)
        
        self.clients: [ClientHandler] = []
    
    def run(self):
        print(f"[SERVER] Starting server on address: {IP}")

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
        print("[SERVER] Server succesfully shut down")
        exit(1)

    def handle_client(self, client: ClientHandler):
        client.set_nickname(client.conn.recv(100).decode(FORMAT))

        if client.nickname == "":
            import random
            client.set_nickname(str(random.randint(10000, 50000)))
        
        print(f"[SERVER] Client {client.nickname} connected")
        self.broadcast(f"--- User {client.nickname} has joined the chat! ---")

        #TODO! dynamic memory for messages
        while client.connected:
            msg = client.conn.recv(1024).decode(FORMAT)
            if msg:
                self.broadcast_msg(client, msg)
                print(f"{client.nickname} sent: {msg}")

                if msg == "!disc":
                    print(f"[SERVER] Client {client.nickname} disconnected")
                    self.broadcast(f"--- User {client.nickname} has disconnected from the chat ---")
                    client.connected = False
                
                elif msg == "!users":
                    clients_str = ""
                    for c in self.clients:
                        clients_str += "[" + c.nickname + "] "
                    client.send_msg(clients_str)
                
                elif msg == "!help":
                    help_str = "Available commands:\n\t!disc - disconnect\n\t!users - show all connected users\n\t!help - show help text"
                    client.send_msg(help_str)
                
                elif msg == "!nick":
                    client.send_msg("Set your new nickname: ")
                    old = client.nickname
                    client.set_nickname(client.conn.recv(100).decode(FORMAT))
                    print(f"[CLIENT] Client {old} changed their username to {client.nickname}")
                    self.broadcast(f"--- User {old} has changed their nickname to {client.nickname} ---")
        
        client.conn.close()
        self.clients.remove(client)

    def broadcast_msg(self, sender, msg):
        self.clients.remove(sender)

        for client in self.clients:
            client.send_msg(sender.nickname + ": " + msg)
        
        self.clients.append(sender)
    
    def broadcast(self, msg):
        for client in self.clients:
            client.send_msg(msg)


server = Server()
server.run()
