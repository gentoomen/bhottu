from api import *
import re

LINK = "Here m8, http://www.duckduckgo.com/?q={}"
NOSEARCH = set([
        ## Might just make this a table instead
        "up",
        "going",
        "happening",
        "with",
        "so",
        "very",
        "a",
        "that",
        "it",
        "your",
])

BINDINGS = set([
        "a",
        "the",
        ])

NOT_ALLOWED = set("?,.")

def load():
    """ Searches terms for users on duckduckgo (with lmddgtfy) """
    registerMessageHandler(None, lmstfy)
registerModule('Lmddgtfy', load)

## Will deal with nested parentheses
def removeParenthezised(string):
    ret = ""; level = 0
    for char in string:
        if char == "(":
            level += 1
        elif char == ")":
            level -= 1
        elif not level:
            ret += char
    return ret

def lmstfy(channel, sender, message):
    match = re.search(r"^what(?:'| i)?s (.+)", message, re.IGNORECASE)
    if match:
        usernames = channelUserList(channel)
        term = removeParenthezised(match.groups()[0])
        term = "".join(
                [char for char in term if char not in NOT_ALLOWED])
        term = re.split(r"\s+", term)
        if term[0] in BINDINGS:
            term = term[1:]
        if not term:
            sendMessage(channel, "Fak u {}".format(sender))
            return
        term = "%20".join(
                [word for word in term if word not in usernames and word])
        sendMessage(channel, LINK.format(term))

