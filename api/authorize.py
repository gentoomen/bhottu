_roots = []
_admins = []

def addRoot(root):
    _roots.append(root)

def addAdmin(admin):
    _admins.append(admin)

def removeAdmin(admin):
    _admins.remove(admin)

def clearAdmins():
    del _admins[:]

def isAuthorized(nickname):
    return nickname in _roots or nickname in _admins
