import socket
import sys
import threading
from commands import Command

# Client configuration
client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5555))

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
        # sys.exit()
    elif command == Command.NICK.value:
        client.send(nickname.encode("utf-8"))
    elif command == Command.PASSW.value:
        client.send(password.encode("utf-8"))
        if client.recv(1024).decode("utf-8") != Command.PASSW_OK.value:
            print("Connection refused (wrong password)")
            stop_thread = True


def is_command(text) -> bool:
    return text in [command.value for command in Command]


# Function to receive messages from the server
def receive_messages():
    while not stop_thread:
        try:
            message = client.recv(1024).decode("utf-8")
            print(message) if not is_command(message) else handle_command(message)
        except:
            client.close()
            return


# Sending messages to the server
def write_messages():
    while not stop_thread:
        try:
            message = input()
            if message.startswith("/"):
                if nickname == "admin":
                    amdin_command(message)
                else:
                    print("Commands can only be executed by an admin.")
            else:
                client.send(message.encode("utf-8"))
        except:
            client.close()
            return

def amdin_command(command: str):
    client.send(command.encode("utf-8"))


# Start threads
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()
write_thread = threading.Thread(target=write_messages)
write_thread.start()
