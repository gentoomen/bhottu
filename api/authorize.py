_roots = []
_admins = []

def addRoot(root):
    _roots.append(root.lower())

def addAdmin(admin):
    _admins.append(admin.lower())

def removeAdmin(admin):
    _admins.remove(admin.lower())

def clearAdmins():
    del _admins[:]

def isAuthorized(nickname):
    return nickname.lower() in _roots or nickname.lower() in _admins
