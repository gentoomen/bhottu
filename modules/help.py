from api import *
from api.stringmatcher import *

def load():
    """Provides help on the bot's commands."""
    registerFunction("help %!S", help, "help [command]")
registerModule('Help', load)

def help(channel, sender, command):
    """Provides help on the bot's commands."""
    msg = ""
    if command == None:
        sendMessage(sender, "The following commands are available:\n"
                            "You can use `help <command>` for specific help.")
        for function in functionList():
            msg += function.name
            if function.restricted and not isAuthorized(sender):
                msg += " || "
                continue
            if function.description == None:
                msg += " || "
            else:
                msg += " => " + function.description + " || "
        sendMessage(sender, "%-20s" %msg)
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