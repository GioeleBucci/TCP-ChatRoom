import socket
import sys
import threading
from typing import Callable, Tuple
from signals import Signal
from commands import Command
from serverutils import *

# admin password (stored in plain text as proof of concept)
admin_password = "password"


def new_client(client: socket.socket, addr):
    try:
        print(f"New connection from {addr}")
        send_command(client, Signal.NICK)
        nickname = receive_message(client)
        if nickname not in clients.values():
            send_command(client, Signal.NICK_OK)
        else:
            close_connection(client)
            return
        if nickname == "admin":
            send_command(client, Signal.PASSW)
            password = receive_message(client)
            if password == admin_password:
                send_command(client, Signal.PASSW_OK)
            else:
                close_connection(client)
                return
        print(f"Nickname of {addr} set to {nickname}")
        server_broadcast(f"{nickname} has joined the chat!")
        clients[client] = nickname
        send_message(client, f"Welcome to the chatroom {nickname}!")
    except:
        print(f"Lost connection from {addr} during login")
        close_connection(client)


# handle a client connection
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
            leftName = clients.get(client, None)
            if leftName is None:
                break
            print(f"Client {leftName} ({addr}) disconnected")
            close_connection(client)
            server_broadcast(f"{leftName} has left the chat!")
            break


"""
a dictionary with the commands that can be executed.
Each command is a tuple with a function and a boolean that indicates if the command is reserved to admin use.
"""
commands_list: dict[str, Tuple[Callable, bool]] = {
    "kick": (Command.kick, True),
    "list": (Command.list, False),
    "msg": (Command.msg, False),
    "whoami": (Command.whoami, False),
    "whois": (Command.whois, True),
}


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
