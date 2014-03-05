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

def lmstfy(channel, sender, message):
    match = re.search(r"^what(?:'| i)?s (.+)", message, re.IGNORECASE)
    if match:
        usernames = channelUserList(channel)
        term = "".join(
                [char for char in match.groups()[0] if char not in NOT_ALLOWED])
        term = re.split(r"\s+", term)
        if term[0] in BINDINGS:
            term = term[1:]
        if not term:
            sendMessage(channel, "Fak u {}".format(sender))
            return
        term = "%20".join(
                [word for word in term if word not in usernames and word])
        sendMessage(channel, LINK.format(term))

