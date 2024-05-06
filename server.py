import socket
import sys
import threading
from typing import Callable, Dict, Tuple
from commands import Command
from utils import send_command, receive_message, send_message, get_address

# clients and nicknames
clients: Dict[socket.socket, str] = {}

admin_password = "password"


def new_client(client: socket.socket, addr):
    print(f"New connection from {addr}")
    send_command(client, Command.NICK)
    nickname = receive_message(client)
    if nickname not in clients.values():
        send_command(client, Command.NICK_OK)
    else:
        send_message(client, "Connection refused (nickname already in use)")
        client.close()
        return
    if nickname == "admin":
        send_command(client, Command.PASSW)
        password = receive_message(client)
        if password == admin_password:
            send_command(client, Command.PASSW_OK)
        else:
            send_message(client, "Connection refused (wrong password)")
            client.close()
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
    close_connection(client)


def process_command(client: socket.socket, command: str):
    command_parts = command[1:].strip().split(" ")
    command_name = command_parts[0]
    args = command_parts[1:]
    if command_name in commands_list:
        fun = commands_list[command_name][0]
        isPrivileged = commands_list[command_name][1]
        if isPrivileged and clients[client] != "admin":
            send_message(client, "This command can only be executed by an admin.")
            return
        fun(client, args)
    else:
        send_message(client, "Invalid command!")


def cmd_kick(client: socket.socket, args: str):
    if len(args) < 2:
        send_message(client, "Syntax: /kick <username> <reason>")
        return
    destUsername = args[0]
    reason = args[1]
    if destUsername in clients.values():
        for user, nickname in clients.items():
            if nickname == destUsername:
                send_message(user, f"You have been kicked for: {reason}")
                send_command(user, Command.KICK)
                close_connection(user)
                server_broadcast(f"{destUsername} has been kicked from the chat.")
                break
    else:
        send_message(client, f"User {destUsername} not found!")


def cmd_list(client: socket.socket, args: str):
    users = "\n".join(clients.values())
    send_message(client, f"Connected users:\n{users}")


def cmd_msg(client: socket.socket, args: str):
    if len(args) < 2:
        send_message(client, "Syntax: /msg <username> <message>")
        return
    destUsername = args[0]
    message = " ".join(args[1:])
    if destUsername in clients.values():
        for user, nickname in clients.items():
            if nickname == destUsername:
                send_message(user, f"{clients[client]} (private message): {message}")
                print(f"{clients[client]} to {destUsername}: {message}")
                break
    else:
        send_message(client, f"User {destUsername} not found!")


def cmd_whoami(client: socket.socket, args: str):
    send_message(client, f"Your nickname is {clients[client]}")


def cmd_whois(client: socket.socket, args: str):
    if len(args) < 1:
        send_message(client, "Syntax: /whois <username>")
        return
    username = args[0]
    if username in clients.values():
        for user, nickname in clients.items():
            if nickname == username:
                send_message(client, f"{username} is {user.getpeername()}")
    else:
        send_message(client, f"User {username} not found!")


"""
a dictionary with the commands that can be executed.
Each command is a tuple with a function and a boolean that indicates if the command is reserved to admin use.
"""
commands_list: Dict[str, Tuple[Callable[[socket.socket, str], None], bool]] = {
    "kick": (cmd_kick, True),
    "list": (cmd_list, False),
    "msg": (cmd_msg, False),
    "whoami": (cmd_whoami, False),
    "whois": (cmd_whois, True),
}


def close_connection(client: socket.socket):
    client.close()
    del clients[client]


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
