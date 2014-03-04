from api import *
import re

LINK = "Here m8, http://www.duckduckgo.com/?q={}"
NOSEARCH = [
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
]

BINDINGS = [
        "a"
        ]

NOT_ALLOWED = set("?,.")

def load():
    """ Searches terms for users on duckduckgo (with lmddgtfy) """
    registerMessageHandler(None, lmstfy)
registerModule('Lmddgtfy', load)

def lmstfy(channel, sender, message):
    match = re.search(r"^what(?:'| i)?s (.+)", message, re.IGNORECASE)
    if match:
        usernames = channelUserList(channel)
        term = "".join(
                [char for char in match.groups()[0] if char not in NOT_ALLOWED]).split(" ")
        if term[0] in BINDINGS:
            term = term[1:]
        term = "%20".join(
                [word for word in term if word not in usernames])
        sendMessage(channel, LINK.format(term))

