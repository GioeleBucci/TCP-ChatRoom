"""Utility functions for both client and server"""

import socket
from typing import List, Tuple

ENCODING = "ascii"


def send_message(client: socket.socket, message: str):
    """Sends a message to a client."""
    client.send(message.encode(ENCODING))

def receive_message(client: socket.socket) -> str:
    """Receives a message from a client."""
    return client.recv(1024).decode(ENCODING)


def get_address(args: List[str]) -> Tuple[str, int]:
    """Extracts the IP address and port number from the command line arguments.
    If such argoments aren't present, defaults to a preset configuration"""
    if len(args) < 3:
        print("IP and port not specified, defaulting to localhost:55555\n")
        return "localhost", 55555
    return args[1], int(args[2])
