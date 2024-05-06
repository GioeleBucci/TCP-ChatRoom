from serverutils import *


class Command:
    def list(client: socket.socket, args: str):
        users = "\n".join(clients.values())
        send_message(client, f"Connected users:\n{users}")

    def msg(client: socket.socket, args: str):
        if len(args) < 2:
            send_message(client, "Syntax: /msg <username> <message>")
            return
        destUsername = args[0]
        message = " ".join(args[1:])
        if destUsername in clients.values():
            for user, nickname in clients.items():
                if nickname == destUsername:
                    send_message(
                        user, f"{clients[client]} (private message): {message}"
                    )
                    print(f"{clients[client]} to {destUsername}: {message}")
                    break
        else:
            send_message(client, f"User {destUsername} not found!")

    def whoami(client: socket.socket, args: str):
        send_message(client, f"Your nickname is {clients[client]}")

    def whois(client: socket.socket, args: str):
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

    def kick(client: socket.socket, args: str):
        if len(args) < 2:
            send_message(client, "Syntax: /kick <username> <reason>")
            return
        destUsername = args[0]
        reason = " ".join(args[1:])
        if destUsername in clients.values():
            for user, nickname in clients.items():
                if nickname == destUsername:
                    send_message(user, f"You have been kicked for: {reason}")
                    send_command(user, Signal.KICK)
                    close_connection(user)
                    server_broadcast(f"{destUsername} has been kicked from the chat.")
                    break
        else:
            send_message(client, f"User {destUsername} not found!")
