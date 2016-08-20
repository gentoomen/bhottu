from api import *

def load():
    dbExecute('CREATE TABLE IF NOT EXISTS autovoice (target VARCHAR(255) UNIQUE )')
    registerFunction('autovoice %s', addAutovoice, restricted=True)
    registerFunction('remove autovoice %s', removeAutovoice, restricted=True)
    registerCommandHandler('JOIN', checkAutovoice)
    registerCommandHandler('MODE', checkAutovoice)

registerModule('AutoVoice', load)

def addAutovoice(channel, sender, target):
    try:
        dbExecute('INSERT INTO autovoice (`target`) VALUES (%s)', [target])
        sendMessage(channel, '%s: %s is now autovoiced.' % (sender, target))
    except Exception:
        sendMessage(channel, '%s: %s is already autovoiced.' % (sender, target))

def removeAutovoice(channel, sender, target):
    if isAutovoice(target):
        dbExecute('DELETE FROM autovoice WHERE `target`=%s', [target])
        sendMessage(channel, '%s: %s is no longer autovoiced.' % (sender, target))
    else:
        sendMessage(channel, '%s: %s is not autovoiced.' % (sender, target))

def isAutovoice(target):
    isAutovoice = dbQuery('SELECT * FROM autovoice WHERE `target`=%s', [target])
    return len(isAutovoice) != 0

def checkAutovoice(args, sender, command):
    if command == 'JOIN':
        (nick, ident, hostname) = parseSender(sender)
        if isAutovoice(nick):
            sendCommand('MODE %s +v %s' % (args[0], nick))
    elif command == 'MODE':
        if len(args) != 3: # #channel -mode target
            return
        channel, mode, target = args
        if mode == '-v' and (isAutovoice(target)):
            sendCommand('MODE %s +v %s' % (channel, target))
