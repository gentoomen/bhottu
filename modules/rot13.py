from api import *

## TODO: Make it so that a user may send a privmsg to the bot
##       requesting rot13, and the bot will then send a public
##       message to everyone in the chatroom.

WRAPS_AROUND_UPPER = "N"
WRAPS_AROUND_LOWER = "n"
MAX_LENGTH = 255

def load():
    registerFunction("rot13 %S", sayRot13, "rot13 <message>")
registerModule("Rot13", load)

def sayRot13(channel, sender, message):
    sendMessage(channel, "{} says, {}".format(sender, rot13Chars(message)))

def rot13Chars(chars):
    """ Pure function that rot13's a string """
    def modChar(char, mod):
        return chr(ord(char) + mod)

    def rot13(char):
        if char.isupper() and char >= WRAPS_AROUND_UPPER:
            return modChar("A", ord(char) - ord(WRAPS_AROUND_UPPER))
        if char.islower() and char >= WRAPS_AROUND_LOWER:
            return modChar("a", ord(char) - ord(WRAPS_AROUND_LOWER))
        if char.islower() or char.isupper():
            return modChar(char, 13)
        else:
            return char

    return "".join(
            [rot13(char) for char in chars])

