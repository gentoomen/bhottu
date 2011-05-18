class Handler(object):
    pass

#
# Handlers registered while a module is being loaded are automatically
# registered as belonging to that loading module, allowing them to be
# automatically unregistered during module unload.
#

_loadingModule = None

def setLoadingModule(module):
    global _loadingModule
    _loadingModule = module

def _effectiveModule(module):
    global _loadingModule
    if module == None:
        return _loadingModule
    return module

#
# A ParsedCommandHandler gets called for each IRC command, in Parse()d form.
#

_parsedCommandHandlers = []

def registerParsedCommandHandler(function, module = None):
    global _parsedCommandHandlers
    registration = Handler()
    registration.enabled = True
    registration.type = _parsedCommandHandlers
    registration.function = function
    registration.module = _effectiveModule(module)
    if registration.module != None:
        registration.module.handlers.append(registration)
    _parsedCommandHandlers.append(registration)
    return registration

#
# Unregisters a ParsedCommandHandler.
#

def unregister(registration):
    global _parsedCommandHandlers
    if registration.type == _parsedCommandHandlers:
        _parsedCommandHandlers.remove(registration)
        registration.enabled = False
        return True
    return False

from time import gmtime, strftime

def Parse(incoming):
    parsed = {}
    tmp_vars = []
    index = 0
    parsed['raw'] = incoming
    parsed['event_timestamp'] = strftime("%H:%M:%S +0000", gmtime())
    for part in parsed['raw'].lstrip(':').split(' '):
        if part.startswith(':'):
            tmp_vars.append(parsed['raw'].lstrip(':')\
                    .split(' ', index)[index].lstrip(':'))
            break
        else:
            tmp_vars.append(part)
            tmp_vars = [' '.join(tmp_vars)]
            index += 1
            continue
    if len(tmp_vars) > 1:
        parsed['event_msg'] = tmp_vars[1]
        cmd_vars = tmp_vars[0].split()
        if cmd_vars[0] == 'PING':
            parsed['event'] = 'PING'
        else:
            parsed['event'] = cmd_vars[1]
            try:
                parsed['event_host'] = cmd_vars[0].split('@')[1]
                parsed['event_user'] = cmd_vars[0].split('@')[0].split('!')[1]
                parsed['event_nick'] = cmd_vars[0].split('@')[0].split('!')[0]
            except:
                parsed['event_host'] = cmd_vars[0]
            if parsed['event'] == 'PRIVMSG':
                    parsed['event_target'] = cmd_vars[2]
    else:
        parsed['event'] = 'silly'
    return parsed

#
# incomingIrcCommand is responsible for acting on incoming irc commands
# by parsing them and calling the appropriate handlers.
#

def incomingIrcCommand(command):
    global _parsedCommandHandlers
    parsed = Parse(command)
    for handler in _parsedCommandHandlers[:]:
        if handler.enabled:
            handler.function(parsed)
