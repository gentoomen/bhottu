from api import *
from api.stringmatcher import *

def load():
    """Provides help on the bot's commands."""
    registerFunction("help %!S", help, "help [command]")
registerModule('Help', load)

def help(channel, sender, command):
    """Provides help on the bot's commands."""
    if command == None:
        sendMessage(sender, "The following commands are available:")
        for function in functionList():
            if function.description == None:
                description = ""
            else:
                description = function.description
            sendMessage(sender, "%-20s %s" % (function.name, description))
        sendMessage(sender, "Use `help <command>` to recieve help on a particular command.")
    else:
        for function in functionList():
            if matchFormat(command, function.attemptFormat) != None:
                helpProvided = False
                if function.description != None:
                    sendMessage(sender, "%s: %s" % (function.name, function.description))
                    helpProvided = True
                if function.syntax != None:
                    sendMessage(sender, "syntax: %s" % function.syntax)
                    helpProvided = True
                if helpProvided:
                    return
        sendMessage(sender, "I have no help on that topic.")
        for function in functionList(): print function.format
