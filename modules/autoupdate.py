from config import *
from utils import *
from api import *
import subprocess

def load():
    registerParsedCommandHandler(AutoUpdate)
registerModule('AutoUpdate', load)

def AutoUpdate(parsed):
    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", it's your birthday"
        if parsed['event_msg'].startswith(combostring):
            if authUser(parsed['event_nick']) == True:
                retcode = subprocess.call(["git", "pull", "origin", "master"])
                if retcode == 0:
                    sendMessage(CHANNEL, "YAY, brb cake!!")
                    sendQuit("mmmmm chocolate cake")
                    subprocess.Popen('./bhottu.py', shell=True)
                else:
                    sendMessage(CHANNEL, "Hmph, no cake!!")
