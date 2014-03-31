## Module for managing other modules, while the bot is running

from api import *

def load():
    """Enable and disable modules on the fly"""
    registerFunction("disable %s", disableModule, "disable <module>", restricted = True)
    registerFunction("enable %s", enableModule, "enable <module>", restricted = True)
registerModule("ManageModules", load)

def disableModule(channel, sender, name):
    if name == "ManageModules":
        sendMessage(channel, "{}: I will not disable ManageModules".format(sender))
    if unloadModule(name):
        sendMessage(channel, "{}: {} has been disabled".format(sender, name))
    else:
        sendMessage(channel, "{}: {} is not loaded".format(sender, name))

def enableModule(channel, sender, name):
    if loadModule(name):
        sendMessage(channel, "{}: {} has been enabled".format(sender, name))
    else:
        sendMessage(channel, "{}: {} does not exist".format(sender, name))

