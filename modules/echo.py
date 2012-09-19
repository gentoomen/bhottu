from api import *

def load():
    """Lets the bot say or shout messages on command."""
    registerFunction("say %S", say, "say <message>")
    registerFunction("shout %S", shout, "shout <message>")
    registerFunction("do %S", do, "do <message>")
registerModule('Echo', load)

def say(channel, sender, message):
    """Say given text."""
    sendMessage(channel, message)

def shout(channel, sender, message):
    """Shout given text."""
    sendMessage(channel, chr(2) + message.upper())

def do(channel, sender, message):
    sendAction(channel, message)
