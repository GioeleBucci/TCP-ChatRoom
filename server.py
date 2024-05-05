import socket
import sys
import threading
from typing import Dict
from commands import Command
from utils import send_command, receive_message, send_message, get_address

# clients and nicknames
clients: Dict[socket.socket, str] = {}

admin_password = "password"


def new_client(client, addr):
    print(f"New connection from {addr}")
    send_command(client, Command.NICK)
    nickname = receive_message(client)
    if nickname == "admin":
        send_command(client, Command.PASSW)
        password = receive_message(client)
        if password == admin_password:
            send_command(client, Command.PASSW_OK)
        else:
            send_message(client, "Connection refused (wrong password)")
            return
    clients[client] = nickname
    print(f"Nickname of {addr} set to {nickname}")
    send_message(client, f"Welcome to the chatroom {nickname}!")
    server_broadcast(f"{nickname} has joined the chat!")


def server_broadcast(message: str):
    print(message)
    for client in clients:
        send_message(client, message)


def client_broadcast(client: socket.socket, message: str):
    formatted_msg = f"{clients[client]}: {message}"
    print(formatted_msg)
    for c in clients:
        if c != client:
            send_message(c, formatted_msg)


# Function to handle each client connection
def handle_client(client: socket.socket, addr):
    new_client(client, addr)
    while True:
        try:
            message = receive_message(client)
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
    if users[admin] != "admin":
        send_message(admin, "Commands can only be executed by an admin.")
        return
    if command.startswith("kick"):
        command_parts = command.split(" ", 2)
        if len(command_parts) < 3:
            send_message(admin, "Syntax: /kick <username> <reason>")
            return
        username = command_parts[1]
        reason = command_parts[2]
        if username in clients.values():
            for client, nickname in clients.items():
                if nickname == username:
                    send_message(client, f"You have been kicked for: {reason}")
                    send_command(client, Command.KICK)
                    client.close()
                    del clients[client]
                    server_broadcast(f"{nickname} has been kicked from the chat.")
                    break
        else:
            send_message(admin, f"User {username} not found!")
    elif command.startswith("list"):
        users = "\n".join(clients.values())
        send_message(admin, f"Connected users:\n{users}")
    else:
        send_message(admin, "Invalid command!")


def server_start():
    # Server configuration
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = get_address(sys.argv)
    server.bind(addr)
    server.listen()
    print(f"Server up on port {addr[1]}")
    # Accept and handle client connections
    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(
            target=handle_client, args=(client_socket, addr)
        )
        client_thread.start()


server_start()
