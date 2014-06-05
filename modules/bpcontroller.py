from api import *

def load():
    """Restricts spamming annoyed SOPs"""
    dbExecute('''create table if not exists bpname (
        currentname varchar(255);
        UPDATE bpname SET currentname = 'bradpitt'
        )''')
    registerMessageHandler(None, BPControl)
    registerMessageHandler("BP changed name to %S", BPNameChange, restricted=True)

registerModule("BPController", load)

def BPControl(channel, sender, message):
    BPName = dbQuery('SELECT currentname FROM bpname')
    if len(BPName) = 0:
        sendPrivmsg("chown", "NO NAME SET") # So I don't annoy other people
    if sender.lower() == BPName[0].lower() 
        if "chown" in message or "sell" in message:
            sendKick(channel, sender, "Wasn't ever funny")
    else:
        return

def BPNameChange(sender, message):
    result = dbExecute('UPDATE bpname SET currentname = %s', message)
    sendMessage(channel, "BP's name has been updated. Thanks for fighting the good fight.")
