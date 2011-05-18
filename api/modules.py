from events import *
import log

class Module(object):
    pass

_modules = {}

def registerModule(name, loadFunction):
    global _modules
    if name in _modules:
        return False
    module = Module()
    module.name = name
    module.loadFunction = loadFunction
    module.description = loadFunction.__doc__
    module.loaded = False
    module.handlers = []
    _modules[name] = module
    return True

def loadModule(name):
    global _modules
    if name not in _modules:
        return False
    module = _modules[name]
    if module.loaded:
        return True
    log.notice('Loading module %s' % name)
    setLoadingModule(module)
    module.loadFunction()
    setLoadingModule(None)
    module.loaded = True
    return True

def unloadModule(name):
    global _modules
    if name not in _modules:
        return False
    module = _modules[name]
    if not module.loaded:
        return True
    log.notice('Unloading module %s' % name)
    for registration in module.handlers:
        unregister(registration)
    module.loaded = False
    return True

def moduleList():
    global _modules
    keys = _modules.keys()
    keys.sort()
    values = []
    for key in keys:
        values.append(_modules[key])
    return values
