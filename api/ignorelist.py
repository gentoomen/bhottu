_ignored = []

def isIgnored(nickname):
    return nickname in _ignored

def addIgnore(nickname):
    global _ignored
    _ignored.append(nickname)

def removeIgnore(nickname):
    global _ignored
    _ignored.remove(nickname)

def clearIgnores():
    global _ignored
    _ignored = []
