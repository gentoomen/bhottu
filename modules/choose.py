from api import *
import random


def load():
    """Requests the bot randomly choose between options given"""
    registerFunction("choose %S", Choose, "choose [option] or [option]...")
registerModule('Choose', load)


def Choose(channel, sender, message):
    """Choose an option"""
    if not "or" in message:
        sendMessage(channel, "Only one option or no options present")
        return
    options = message.Split("or")
    sendMessage(channel, random.Choice(options).strip())
