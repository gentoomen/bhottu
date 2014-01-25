import events
import log

class Module(object):
    pass

_modules = {}

def registerModule(name, loadFunction):
    if name in _modules:
        return False
    module = Module()
    module.name = name
    module.loadFunction = loadFunction
    module.description = loadFunction.__doc__
    module.loaded = False
    module.handlers = []
    module.unloadHandlers = []
    _modules[name] = module
    return True

# Decorator for syntax sugar
def registerMod(name):
    def registerMod_deco(loadFunction):
        registerModule(name, loadFunction)
    return registerMod_deco

def loadModule(name):
    if name not in _modules:
        return False
    module = _modules[name]
    if module.loaded:
        return True
    log.notice('Loading module %s' % name)
    events.setLoadingModule(module)
    module.loadFunction()
    events.setLoadingModule(None)
    module.loaded = True
    return True

def unloadModule(name):
    if name not in _modules:
        return False
    module = _modules[name]
    if not module.loaded:
        return True
    log.notice('Unloading module %s' % name)
    events.moduleUnloadEvent(module)
    for registration in module.handlers[:]:
        events.unregister(registration)
    module.loaded = False
    return True

def moduleList():
    keys = _modules.keys()
    keys.sort()
    values = []
    for key in keys:
        values.append(_modules[key])
    return values
