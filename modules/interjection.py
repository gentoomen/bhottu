from api import *
import re

def load():
    """Corrects users on incorrect use of terminology."""
    registerMessageHandler(None, interject)
registerModule('Interjection', load)

def interject(channel, sender, message):
    if re.search('\\blinux\\b', message, re.IGNORECASE):
        sendMessage(channel, "I would just like to interject for a moment, what you know as Linux is in fact, GNU/Linux or as I have taken to calling it, Unity.")
