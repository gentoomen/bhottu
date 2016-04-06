from api import *
import random


def load():
    """ Kicking and banning management through the bot. """
    dbExecute('''create table if not exists autobans (
              banID int auto_increment primary key,
              `nick` varchar(255) )''')
    registerFunction("kick %S", kickUser, restricted=True)
    registerFunction("ban %S", banUser, restricted=True)
    registerFunction("unban %s", unbanUser, restricted=True)
    registerFunction("autoban %s", autoBan, restricted=True)
    registerFunction("clear bans", clearBans, restricted=True)
    registerFunction("list bans", listBans)
    registerCommandHandler("JOIN", checkBan)
registerModule("KickBan", load)


replies = ("someone must not like you at all", "oops, my bad",
           "I am really, really sorry")


def kickUser(channel, sender, target):
    split = target.split(";")
    for user in split[0].strip().split():
        try:
            sendKick(channel, user, split[1].strip())
        except IndexError:
            sendKick(channel, user, random.choice(replies))


def banUser(channel, sender, target):
    targets = target.split()
    if len(targets) == 4 and targets[1] == 'for' and targets[2].isdigit() and targets[3].rstrip('s') in ('second', 'minute', 'hour', 'day', 'week', 'month', 'year'):
        sendMessage(channel, '%s: did you mean: tempban %s' % (sender, target))
        return
    for user in targets():
        sendKick(channel, user, random.choice(replies))
        sendCommand("MODE %s +b %s" % (channel, user))


def autoBan(channel, sender, target):
    alreadyBanned = dbQuery('SELECT banID FROM autobans WHERE `nick`=%s',
                            [target])
    if len(alreadyBanned) != 0:
        sendMessage(channel, "%s: %s is already auto banned." % (sender,
                    target))
    else:
        sendKick(channel, target, random.choice(replies))
        sendCommand("MODE %s +b %s" % (channel, target))
        dbExecute('INSERT INTO autobans (`nick`) VALUES (%s)', [target])


def listBans(channel, sender):
    bannedUsers = dbQuery('SELECT banID, `nick` from autobans')
    if len(bannedUsers) > 0:
        listUsers = ""
        for banID, nick in bannedUsers:
            listUsers = listUsers + "%s, " % nick
        sendMessage(channel, "%s: %s" % (sender, listUsers))
    else:
        sendMessage(channel, "No auto bans set.")


def unbanUser(channel, sender, target):
    isBanned = dbQuery('SELECT banID FROM autobans WHERE `nick`=%s',
                       [target])
    if len(isBanned) > 0:
        sendCommand("MODE %s -b %s" % (channel, target))
        dbExecute('DELETE FROM autobans WHERE `nick`=%s', [target])


def clearBans(channel):
    bans = dbQuery('SELECT banID, `nick` from autobans')
    for banID, nick in bans:
        sendCommand("MODE %s -b %s" % (channel, nick))
    dbExecute('DELETE FROM autobans')
    sendMessage(channel, "Cleared all bans.")


def checkBan(channel, sender):
    (nick, ident, hostname) = parseSender(sender)
    isBanned = dbQuery('SELECT banID FROM autobans WHERE `nick`=%s', [nick])
    if len(isBanned) > 0:
        sendKick(channel[0], nick, random.choice(replies))
        sendCommand("MODE %s +b %s" % (channel[0], nick))
