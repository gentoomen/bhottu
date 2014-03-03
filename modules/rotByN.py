from api import *

## TODO: Make it so that a user may send a privmsg to the bot
##       requesting rot13, and the bot will then send a public
##       message to everyone in the chatroom.

MAX_LENGTH = 255

def load():
    registerFunction("rot%i %S", sayRotN, "rot<places> <message>")
registerModule("Rot13", load)

def sayRotN(channel, sender, places, message):
    if places > 13:
        sendMessage(channel, "May not rotate by more than 13 places")
        return
    sendMessage(channel, "{} says, {}".format(sender, rotNChars(message, places)))

def rotNChars(chars, n):
    """ Pure function which "rotates" a strings alphabetic characters """

    if n > 13:
        raise TypeError("May not rotate by more than 13 places")

    def modChar(char, mod):
        return chr(ord(char) + mod)

    WRAPS_AROUND_LOWER = modChar("a", n)
    WRAPS_AROUND_UPPER = modChar("A", n)

    def rotN(char, n):
        if char.isupper() and char >= WRAPS_AROUND_UPPER:
            return modChar("A", ord(char) - ord(WRAPS_AROUND_UPPER))
        if char.islower() and char >= WRAPS_AROUND_LOWER:
            return modChar("a", ord(char) - ord(WRAPS_AROUND_LOWER))
        if char.islower() or char.isupper():
            return modChar(char, n)
        else:
            return char

    return "".join(
            [rotN(char, n) for char in chars])

