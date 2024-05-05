import socket
import threading
from typing import Dict
from commands import Command

# clients and nicknames
clients: Dict[socket.socket, str] = {}

admin_password = "password"


def new_client(client, addr):
    print(f"New connection from {addr}")
    client.send(Command.NICK.value.encode("utf-8"))
    nickname = client.recv(1024).decode("utf-8")
    if nickname == "admin":
        client.send(Command.PASSW.value.encode("utf-8"))
        password = client.recv(1024).decode("utf-8")
        if password == admin_password:
            client.send(Command.PASSW_OK.value.encode("utf-8"))
        else:
            client.send("Incorrect password!".encode("utf-8"))
            return
    clients[client] = nickname
    print(f"Nickname of {addr} set to {nickname}")
    client.send(f"Welcome to the chatroom {nickname}!".encode("utf-8"))
    server_broadcast(f"{nickname} has joined the chat!")


def server_broadcast(message: str):
    print(message)
    for client in clients:
        client.send(message.encode("utf-8"))


def client_broadcast(client: socket.socket, message: str):
    formatted_msg = f"{clients[client]}: {message}"
    print(formatted_msg)
    for c in clients:
        if c != client:
            c.send((formatted_msg).encode("utf-8"))


# Function to handle each client connection
def handle_client(client: socket.socket, addr):
    new_client(client, addr)
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            if message.startswith("/"):
                process_command(client, message)
            else:
                client_broadcast(client, message)
        except:
            print(f"Client {addr} disconnected")
            server_broadcast(f"{clients[client]} has left the chat!")
            break
    # Close the connection with the client
    client.close()
    del clients[client]


def process_command(admin: socket.socket, command: str):
    command = command[1:].strip()  # normalize command
    if command.startswith("kick"):
        command_parts = command.split(" ", 2)
        if len(command_parts) < 3:
            admin.send("Invalid syntax: /kick <username> <reason>".encode("utf-8"))
            return
        username = command_parts[1]
        reason = command_parts[2]
        if username in clients.values():
            for client, nickname in clients.items():
                if nickname == username:
                    client.send(f"You have been kicked for: {reason}".encode("utf-8"))
                    client.send(Command.KICK.value.encode("utf-8"))
                    client.close()
                    del clients[client]
                    server_broadcast(f"{nickname} has been kicked from the chat.")
                    break
        else:
            admin.send(f"User {username} not found!".encode("utf-8"))
    elif command.startswith("list"):
        users = "\n".join(clients.values())
        admin.send(f"Connected users:\n{users}".encode("utf-8"))
    else:
        admin.send("Invalid command!".encode("utf-8"))


def server_start():
    # Server configuration
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 5555))
    server.listen()
    print("Server listening...")
    # Accept and handle client connections
    while True:
        client_socket, addr = server.accept()
        # clients.append(client_socket)
        client_thread = threading.Thread(
            target=handle_client, args=(client_socket, addr)
        )
        client_thread.start()


server_start()
