_ignored = []

def isIgnored(nickname):
    return nickname.lower() in _ignored

def addIgnore(nickname):
    global _ignored
    _ignored.append(nickname.lower())

def removeIgnore(nickname):
    global _ignored
    _ignored.remove(nickname.lower())

def clearIgnores():
    global _ignored
    _ignored = []
