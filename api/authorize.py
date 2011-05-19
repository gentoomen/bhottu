_roots = []

def addRoot(root):
    global _roots
    _roots.append(root)

def isAuthorized(nickname):
    return nickname in _roots
