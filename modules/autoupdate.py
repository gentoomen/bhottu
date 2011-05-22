from api import *
import subprocess
import os

def load():
    """Allows the bot to update itself."""
    registerFunction("it's your birthday", birthday, restricted = True)
registerModule('AutoUpdate', load)

def birthday(channel):
    """Updates the bot to the latest version."""
    result = subprocess.call(["git", "pull", "origin", "master"])
    if result == 0:
        sendMessage(channel, "YAY, brb cake!!")
        sendQuit("mmmmm chocolate cake")
        os.execl("./bhottu.py", "./bhottu.py")
    else:
        sendMessage(channel, "Hmph, no cake!!")
