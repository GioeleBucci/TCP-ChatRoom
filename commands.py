from enum import Enum

class Command(Enum):
    NICK = "NICK" # ask for nickname
    PASSW = "PASSW" # ask for password
    PASSW_OK = "PASSW_OK" # password is correct
    KICK = "KICK" # kick a user

