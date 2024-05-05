from enum import Enum

class Command(Enum):
    KICK = "KICK" # kick a user
    PASSW = "PASSW" # ask for password
    PASSW_OK = "PASSW_OK" # password is correct
    NICK = "NICK" # ask for nickname

