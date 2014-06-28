from api import *

## TODO: Make it so that a user may send a privmsg to the bot
##       requesting rot13, and the bot will then send a public
##       message to everyone in the chatroom.

MAX_LENGTH = 255

def load():
    registerFunction("rot%i %S", sayRotN, "rot<places> <message>")
registerModule("RotByN", load)

def sayRotN(channel, sender, places, message):
    if places > 13 or places < 1:
        sendMessage(channel, "May not rotate by more than 13 places or less than one place")
        return
    sendMessage(channel, "{} says, {}".format(sender, rotNChars(message, places)))

def rotNChars(chars, n):
    """ Pure function which "rotates" a strings alphabetic characters """

    if n > 13 or n < 1:
        raise TypeError("May not rotate by more than 13 places or less than one place")

    def modChar(char, mod):
        return chr(ord(char) + mod)

    WRAPS_AROUND_LOWER = modChar("a", 26 - n)
    WRAPS_AROUND_UPPER = modChar("A", 26 - n)

    def rotN(char, n):
        if char.isupper() and char >= WRAPS_AROUND_UPPER:
            return modChar("A", ord(char) - ord(WRAPS_AROUND_UPPER))
        if char.islower() and char >= WRAPS_AROUND_LOWER:
            return modChar("a", ord(char) - ord(WRAPS_AROUND_LOWER))
        if char.isalpha():
            return modChar(char, n)
        return char

    return "".join(
            [rotN(char, n) for char in chars])

