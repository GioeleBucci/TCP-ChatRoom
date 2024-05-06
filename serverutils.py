"""Utility module for the server only."""

import socket
from signals import Signal
from typing import Dict
from utils import *

# clients and nicknames
clients: Dict[socket.socket, str] = {}


def send_command(client: socket.socket, command: Signal):
    """Sends a command to a client."""
    client.send(command.value.encode(ENCODING))


def server_broadcast(message: str):
    """Sends a message to all clients"""
    print(message)
    for client in clients:
        send_message(client, message)


def client_broadcast(client: socket.socket, message: str):
    """Sends a message to all other clients"""
    formatted_msg = f"{clients[client]}: {message}"
    print(formatted_msg)
    for c in clients:
        if c != client:
            send_message(c, formatted_msg)


def close_connection(client: socket.socket):
    client.shutdown(socket.SHUT_RDWR)
    client.close()
    if client in clients:
        del clients[client]
