import socket
import threading
import sys
from utils import receive_message, send_message, get_address
from commands import Command

# Client configuration
client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(get_address(sys.argv))

# global variables
stop_thread: bool = False
nickname: str = input("Enter nickname: ").strip()
if nickname == "admin":
    password: str = input("Enter password: ")


def handle_command(command):
    if command == Command.KICK.value:
        print("Kicked from chatroom.")
        global stop_thread
        stop_thread = True
    elif command == Command.NICK.value:
        send_message(client, nickname)
        if receive_message(client) != Command.NICK_OK.value:
            print("Connection refused (nickname already in use)")
            stop_thread = True
    elif command == Command.PASSW.value:
        send_message(client, password)
        if receive_message(client) != Command.PASSW_OK.value:
            print("Connection refused (wrong password)")
            stop_thread = True


# Function to receive messages from the server
def receive_messages():
    while not stop_thread:
        try:
            message = receive_message(client)
            print(message) if not is_command(message) else handle_command(message)
        except:
            client.close()
            return


def is_command(text) -> bool:
    return text in [command.value for command in Command]


# Sending messages to the server
def write_messages():
    while not stop_thread:
        try:
            message = input()
            send_message(client, message)
        except:
            client.close()
            return


# Start threads
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()
write_thread = threading.Thread(target=write_messages)
write_thread.start()
