from api import *
import api
import time
import string

def load():
    dbExecute('''create table if not exists admins (
              adminID int auto_increment primary key,
              nick varchar(255),
              issuer varchar(255),
              issuetime int,
              unique(nick) )''')
    for admin in dbQuery("SELECT nick FROM admins"):
        registerAdmin(admin)
    registerFunction("add admin %s", addAdmin, "add admin <nickname>", restricted = True)
    registerFunction("remove admin %s", removeAdmin, "remove admin <nickname>", restricted = True)
    registerFunction("list admins", listAdmins, "list admins", restricted = False)
registerModule('Admins', load)

def addAdmin(channel, sender, target):
    """Adds an admin"""
    if len(dbQuery("SELECT nick FROM admins WHERE nick=%s", [target])) > 0:
        sendMessage(channel, "%s is already an admin." % (sender))
        return
    timestamp = int(time.time())
    dbExecute("INSERT INTO admins (nick, issuer, issuetime) VALUES (%s, %s, %s)", [target, sender, timestamp])
    registerAdmin(target)
    sendMessage(channel, "%s added as an admin by %s." % (target, sender))
    log.info('%s added as an admin by %s.' % (target, sender))
    return
    
    
def removeAdmin(channel, sender, target):
    """Removes an admin"""
    if len(dbQuery("SELECT nick FROM admins WHERE nick=%s", [target])) <= 0:
        sendMessage(channel, "There is no such admin as %s." % (target))
        return
    if target == sender:
        dbExecute("DELETE FROM admins WHERE nick=%s", [target])
        sendMessage(channel, "Trying to remove yourself, huh? Too bad the if statement checking for that is down at the workshop.")
        log.info('Silly %s, removing himself from the admins...' % (sender))
        return
    dbExecute("DELETE FROM admins WHERE nick=%s", [target])
    unregisterAdmin(target)
    sendMessage(channel, "%s's admin status was removed by %s." % (target, sender))
    log.info('%s\'s admin status was removed by %s.' % (target, sender))
    return
    
    
def listAdmins(channel, sender):
    if len(dbQuery("SELECT nick FROM admins")) <= 0:
        sendMessage(channel, "There are no admins yet.")
        return
    sendMessage(sender, "The following people are admins: ")
    for (nick, issuer, issuetime) in dbQuery("SELECT nick, issuer, issuetime FROM admins"):
        sendMessage(sender, "%s: set by %s on %s" % (nick, issuer, time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(issuetime))))
    return
    

