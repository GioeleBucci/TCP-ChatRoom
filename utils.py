"""Utility functions for the correct communication between client and server"""

import socket
from typing import List, Tuple
from commands import Command

ENCODING = "utf-8"


def send_message(client: socket.socket, message: str):
    client.send(message.encode(ENCODING))


def send_command(client: socket.socket, command: Command):
    client.send(command.value.encode(ENCODING))


def receive_message(client: socket.socket) -> str:
    return client.recv(1024).decode(ENCODING)


def get_address(args: List[str]) -> Tuple[str, int]:
    if len(args) < 3:
        print("IP and port not specified, defaulting to localhost:55555\n")
        return "localhost", 55555
    return args[1], int(args[2])
