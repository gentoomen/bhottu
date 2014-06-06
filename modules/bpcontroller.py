from api import *

_currentName = "bradpitt"

def load():
    """Restricts spamming annoyed SOPs"""
    registerMessageHandler(None, BPControl)
    registerMessageHandler("BP changed name to %S", BPNameChange, restricted=True)

registerModule("BPController", load)

def BPControl(channel, sender, message):
    if sender.lower() == _currentName.lower():
        if "chown" in message or "sell" in message:
            sendKick(channel, sender, "Wasn't ever funny")
            
def BPNameChange(sender, message):
    global _currentName
    _currentName = message
    sendMessage(channel, "BP's name has been updated. Thanks for fighting the good fight.")
