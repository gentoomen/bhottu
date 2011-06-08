from api import *
import time

def load():
    dbExecute('''create table if not exists admins (
              adminID int auto_increment primary key,
              nick varchar(255),
              issuer varchar(255),
              issuetime int,
              unique(nick) )''')
    for (admin, ) in dbQuery("SELECT nick FROM admins"):
        authorize.addAdmin(admin)
    registerFunction("add admin %s", addAdmin, "add admin <nickname>", restricted = True)
    registerFunction("remove admin %s", removeAdmin, "remove admin <nickname>", restricted = True)
    registerFunction("list admins", listAdmins, "list admins")
    registerUnloadHandler(clearAdmins)
registerModule('Admins', load)

def addAdmin(channel, sender, target):
    """Adds an admin"""
    if len(dbQuery("SELECT nick FROM admins WHERE nick=%s", [target])) > 0:
        sendMessage(channel, "%s is already an admin." % (target))
        return
    timestamp = int(time.time())
    dbExecute("INSERT INTO admins (nick, issuer, issuetime) VALUES (%s, %s, %s)", [target, sender, timestamp])
    authorize.addAdmin(target)
    sendMessage(channel, "Added %s as an admin." % (target))
    log.notice('%s added as an admin by %s.' % (target, sender))

def removeAdmin(channel, sender, target):
    """Removes an admin"""
    if len(dbQuery("SELECT nick FROM admins WHERE nick=%s", [target])) <= 0:
        sendMessage(channel, "There is no such admin." % (target))
        return
    dbExecute("DELETE FROM admins WHERE nick=%s", [target])
    authorize.removeAdmin(target)
    sendMessage(channel, "Removed %s as an admin." % (target))
    log.notice('%s\'s admin status was removed by %s.' % (target, sender))

def listAdmins(channel, sender):
    """Lists all the current bhottu admins"""
    if len(dbQuery("SELECT nick FROM admins")) <= 0:
        sendMessage(sender, "There are no admins yet.")
        return
    sendMessage(sender, "The following people are admins: ")
    for (nick, issuer, issuetime) in dbQuery("SELECT nick, issuer, issuetime FROM admins"):
        sendMessage(sender, "%s: set by %s on %s" % (nick, issuer, time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(issuetime))))
