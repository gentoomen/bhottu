from api import *
import re

name_mappings = {}

def load():
    """Restricts spamming annoyed SOPs"""
    dbExecute('''create table if not exists controlledusers (
              userID int auto_increment primary key,
              nick varchar(255),
              regex varchar(255),
              alternate_nick varchar(255)
              )''')
    registerFunction("control %s %S", add_controlled_user, "control <nick> <regex>", restricted=True)
    registerFunction("control alt %s as %S", add_alternate_controlled_nick,
                     "control alt <alternate_nick> as <original_nick>", restricted=True)
    registerFunction("stop controlling %S", stop_control_user, "stop controlling <nick>", restricted=True)
    registerFunction("update control %s %S", update_control_regex, "update control <nick> <regex>", restricted=True)
    registerMessageHandler(None, BPControl)
    load_controlled_nicks()


registerModule("BPController", load)

def load_controlled_nicks():
    global name_mappings
    print "NAME MAPPINGS: {}".format(name_mappings)
    currently_controlled = dbQuery("SELECT nick, regex, alternate_nick FROM controlledusers")
    print "CONTROLLED: {}".format(currently_controlled)
    for (nick, regex, alternate_nick) in currently_controlled:
        print "Nick: {} regex: {} alternate_nick: {}".format(nick, regex, alternate_nick)
        name_mappings[nick.lower()] = regex
        if alternate_nick not in [None, ""]:
            alt_nick_lower = alternate_nick.lower()
            if alt_nick_lower in name_mappings and name_mappings[alt_nick_lower] not in [None, ""]:
                name_mappings[nick.lower()] = name_mappings[alt_nick_lower]
            else:
                name_mappings[nick.lower()] = ""


def add_controlled_user(channel, sender, user_to_control, regex):
    currently_controlled = dbQuery("SELECT nick FROM controlledusers WHERE nick=%s", [user_to_control])
    if len(currently_controlled) > 0:
        sendMessage(channel, "{} is already in my database".format(user_to_control))
        return
    dbExecute("INSERT INTO controlledusers (nick, regex) VALUES (%s, %s)", [user_to_control.strip(), regex])
    load_controlled_nicks()
    sendMessage(channel, "{}: BradPitt^W {} is now being controlled".format(sender, user_to_control))

def stop_control_user(channel, sender, user_to_control):
    currently_controlled = dbQuery("SELECT nick FROM controlledusers WHERE nick=%s", [user_to_control])
    if len(currently_controlled) == 0:
        sendMessage(channel, "{} is not in my database".format(user_to_control))
        return
    dbExecute("DELETE from controlledusers WHERE nick=%s", [user_to_control])
    load_controlled_nicks()
    sendMessage(channel, "Did {} start acting like a normal person then?".format(user_to_control))

def add_alternate_controlled_nick(channel, sender, alt_nick, original_nick):
    currently_controlled = dbQuery("SELECT nick FROM controlledusers WHERE nick=%s", [alt_nick])
    if len(currently_controlled) > 0:
        sendMessage(channel, "{} is already in my database".format(alt_nick))
        return
    dbExecute("INSERT INTO controlledusers (nick, alternate_nick) VALUES (%s, %s)", [alt_nick, original_nick])
    load_controlled_nicks()
    sendMessage(channel, "BP's^H^H^H^H {}'s name has been updated. Thanks for fighting the good fight".format(original_nick))

def update_control_regex(channel, sender, controlled_user, regex):
    currently_controlled = dbQuery("SELECT nick FROM controlledusers WHERE nick=%s", [controlled_user])
    if len(currently_controlled) == 0:
        sendMessage(channel, "{} is not in my database".format(controlled_user))
        return
    dbExecute("UPDATE controlledusers SET regex=%s WHERE nick=%s", [regex, controlled_user])
    load_controlled_nicks()
    sendMessage(channel, "Updated {} regex to {}".format(controlled_user, regex))

def BPControl(channel, sender, message):
    print "NAME MAPPINGS: {}".format(name_mappings)
    if sender.lower() in name_mappings:
        if re.search(name_mappings[sender.lower()], message, re.UNICODE + re.IGNORECASE):
            sendMessage(channel, "MATCH {} on {}".format(sender, name_mappings[sender.lower()]))
            sendKick(channel, sender, "Wasn't ever funny")
