from api import *
from api.stringmatcher import *
from utils import pastebins

def load():
    """Provides help on the bot's commands."""
    registerFunction("help %!S", help, "help [command]")
registerModule('Help', load)

def help(channel, sender, command):
    """Provides help on the bot's commands."""
    msg_lines = []
    if command == None:
        msg_lines.append("The following commands are available:")
        for function in functionList():
            syntax = function.syntax
            if function.description:
                description = "|| " + function.description
            else:
                description = ""
            if function.restricted:
                admin_command = "(admin command)"
            else:
                admin_command = ""
            # If there is no syntax for the command documented, then why use it?
            if syntax is not None:
                command_line = "{} {} {}".format(syntax, description, admin_command)
                msg_lines.append(command_line)
        msg_lines.append("You can use `help <command>` for specific help.")
        msg = "\n\n".join(msg_lines)
        url = pastebins.paste(msg)
        sendMessage(channel, "{}: {}".format(sender, url))

    else:
        for function in functionList():
            if matchFormat(command, function.format) != None:
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
