_roots = []
_admins = []

def addRoot(root):
    global _roots
    _roots.append(root)
    
def registerAdmin(admin):
    global _admins
    _admins.append(admin)
    
def unregisterAdmin(admin):
    global _admins
    _admins.remove(admin)
    
def isAuthorized(nickname):
    return nickname in _roots or _admins
