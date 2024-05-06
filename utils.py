"""Utility functions for the correct communication between client and server"""

import socket
from typing import List, Tuple
from signals import Signal

ENCODING = "ascii"


def send_message(socket: socket.socket, message: str):
    """Sends a message to a socket."""
    socket.send(message.encode(ENCODING))


def send_command(socket: socket.socket, command: Signal):
    """Sends a command to a socket."""
    socket.send(command.value.encode(ENCODING))


def receive_message(socket: socket.socket) -> str:
    """Receives a message from a socket."""
    return socket.recv(1024).decode(ENCODING)


def get_address(args: List[str]) -> Tuple[str, int]:
    """Extracts the IP address and port number from the command line arguments.
    If such argoments aren't present, defaults to a preset configuration"""
    if len(args) < 3:
        print("IP and port not specified, defaulting to localhost:55555\n")
        return "localhost", 55555
    return args[1], int(args[2])
