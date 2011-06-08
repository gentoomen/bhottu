_roots = []
_admins = []

def addRoot(root):
    global _roots
    _roots.append(root)
    
def addAdmin(admin):
    global _admins
    _admins.append(admin)
    
def removeAdmin(admin):
    global _admins
    _admins.remove(admin)
    
def clearAdmins():
    global _admins
    _admins = []
    
def isAuthorized(nickname):
    return nickname in _roots or nickname in _admins
