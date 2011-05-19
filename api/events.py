import stringmatcher

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
# A ParsedEventHandler gets called for each IRC event, in Parse()d form.
#

_parsedEventHandlers = []

def registerParsedEventHandler(function, module = None):
    global _parsedEventHandlers
    registration = Handler()
    registration.enabled = True
    registration.type = _parsedEventHandlers
    registration.function = function
    registration.module = _effectiveModule(module)
    if registration.module != None:
        registration.module.handlers.append(registration)
    _parsedEventHandlers.append(registration)
    return registration

#
# An CommandHandler gets called for each IRC event with the given command.
# `function` is called as function([arguments[, sender[, command]]]),
# where `arguments` is the list of event arguments, `sender` is the sender
# of the event (which may be the hostname of the server, the nickname of the person, or None),
# and `command` is the event command.
#

_commandHandlers = {}

def registerCommandHandler(command, function, module = None):
    """Registers a function for a given IRC command.
       If command == None, the function is registered for ALL incoming IRC events.
    """
    global _commandHandlers
    registration = Handler()
    registration.enabled = True
    registration.type = _commandHandlers
    registration.command = command
    registration.function = function
    registration.module = _effectiveModule(module)
    if registration.module != None:
        registration.module.handlers.append(registration)
    if command not in _commandHandlers:
        _commandHandlers[command] = []
    _commandHandlers[command].append(registration)
    return registration

#
# A Function gets called for each IRC message matching its format specifier.
# For details of the format specifier system, see stringmatcher.py.
# Function format specifier must start with a literal.
#
# `function` is called as function([channel [, sender [, argument1 [, argument2 ...]]]]),
# where `sender` is the nickname of the person sending the message,
# `channel` is the channel in which the message was spoken OR
#    (in case of a private message) the nickname of the sender (i.e. a copy of `sender`),
# and argument1..N are the matched values of the format specifier.
#

_functionHandlers = []

def registerFunction(format, function, syntax = None, module = None, implicit = False, restricted = False, errorMessages = True):
    global _functionHandlers
    parsedFormat = stringmatcher.parseFormat(format)
    name = _functionName(parsedFormat)
    registration = Handler()
    registration.enabled = True
    registration.type = _functionHandlers
    registration.function = function
    registration.module = _effectiveModule(module)
    registration.format = parsedFormat
    registration.name = name
    registration.description = function.__doc__
    registration.syntax = syntax
    registration.implicit = implicit
    registration.restricted = restricted
    registration.errorMessages = errorMessages
    if registration.module != None:
        registration.module.handlers.append(registration)
    _functionHandlers.append(registration)
    return registration

def _functionName(format):
    output = ''
    if len(format) == 0 or format[0][0] != 'literal':
        raise ValueError, 'Invalid function format'
    for (type, argument) in format:
        if type == 'literal':
            output += argument
        elif type == 'space':
            output += ' '
        else:
            # Remove everything from the last space onwards.
            # This takes care of syntax that is not part of the command,
            # like 'quote <%s> %S'.
            pos = output.rfind(' ')
            if pos < 0:
                return output
            return output[pos:]
    return output

#
# A MessageHandler uses the same syntax as a Function, but need not start with
# a literal; it also doesn't automatically appear in the help system,
# generate syntax hints, and stuff like that.
#

_messageHandlers = []

def registerMessageHandler(format, function, module = None, implicit = False):
    global _messageHandlers
    parsedFormat = stringmatcher.parseFormat(format)
    registration = Handler()
    registration.enabled = True
    registration.type = _functionHandlers
    registration.function = function
    registration.module = _effectiveModule(module)
    registration.format = parsedFormat
    registration.implicit = implicit
    if registation.module != None:
        registration.module.handlers.append(registration)
    _messageHandlers.append(registration)
    return registration

#
# Unregisters a ParsedCommandHandler, EventHandler, FunctionHandler, or MessageHandler.
#

def unregister(registration):
    global _parsedEventHandlers
    if registration.type == _parsedEventHandlers:
        _parsedEventHandlers.remove(registration)
        registration.enabled = False
        return True
    global _commandHandlers
    if registration.type == _commandHandlers:
        _commandHandlers[registration.command].remove(registration)
        return True
    global _functionHandlers
    if registration.type == _functionHandlers:
        _functionHandlers.remove(registration)
        return True
    global _messageHandlers
    if registration.type == _messageHandlers:
        _messageHandlers.remove(registration)
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

def parseEvent(event):
    if event[:1] == ':':
        pos = event.find(' ')
        if pos < 0:
            return None
        sender = event[1:pos]
        remainder = event[pos+1:].lstrip(' ')
    else:
        sender = None
        remainder = event
    
    pos = remainder.find(' ')
    if pos < 0:
        command = remainder
        remainingArguments = ''
    else:
        command = remainder[:pos]
        remainingArguments = remainder[pos+1:].lstrip(' ')
    
    arguments = []
    while remainingArguments != '':
        if remainingArguments[0] == ':':
            arguments.append(remainingArguments[1:])
            remainingArguments = ''
        else:
            pos = remainingArguments.find(' ')
            if pos < 0:
                arguments.append(remainingArguments)
                remainingArguments = ''
            else:
                arguments.append(remainingArguments[:pos])
                remainingArguments = remainingArguments[pos+1:].lstrip(' ')
    return (sender, command, arguments)

#
# Calls a function with (up to) as many arguments as it accepts.
#

def callFunction(function, arguments):
    function(*arguments[:function.func_code.co_argcount])

#
# incomingIrcEvent is responsible for acting on incoming irc events
# by parsing them and calling the appropriate handlers.
#

def incomingIrcEvent(event):
    parsed = Parse(event)
    global _parsedEventHandlers
    for handler in _parsedEventHandlers[:]:
        if not handler.enabled:
            continue
        handler.function(parsed)
    
    (sender, command, arguments) = parseEvent(event)
    global _commandHandlers
    if None in _commandHandlers:
        for handler in _commandHandlers[None][:]:
            if not handler.enabled:
                continue
            callFunction(handler.function, [arguments, sender, command])
    if command in _commandHandlers:
        for handler in _commandHandlers[command][:]:
            if not handler.enabled:
                continue
            callFunction(handler.function, [arguments, sender, command])
    if command == 'PRIVMSG':
        incomingIrcMessage(sender, arguments)

#
# TODO:
#
# - respond only on "$nick, " unless handler.implicit is set
# - respond only to authorized users if handlers.restricted is set
# - deliver syntax hints
#

def incomingIrcMessage(sender, arguments):
    # sender is a nickname!ident@hostname triple.
    (nickname, ident, hostname) = parseSender(sender)
    channel = arguments[0]
    message = arguments[1]
    if channel[0] != '#' and channel[0] != '&':
        channel = nickname
    
    
    global _functionHandlers
    for handler in _functionHandlers[:]:
        if not handler.enabled:
            continue
        arguments = stringmatcher.matchFormat(message, handler.format)
        if isinstance(arguments, list):
            callFunction(handler.function, [channel, nickname] + arguments)
        elif arguments == True:
            # TODO: Send syntax hint
            pass
    global _messageHandlers
    for handler in _messageHandlers[:]:
        if not handler.enabled:
            continue
        arguments = stringmatcher.matchFormat(message, handler.format)
        if isinstance(arguments, list):
            callFunction(handler.function, [channel, nickname] + arguments)

def parseSender(sender):
    pos = sender.find('@')
    if pos < 0:
        hostname = None
        nickIdent = sender
    else:
        hostname = sender[pos+1:]
        nicknameIdent = sender[:pos]
    pos = nicknameIdent.find('!')
    if pos < 0:
        ident = None
        nickname = nicknameIdent
    else:
        ident = nicknameIdent[pos+1:]
        nickname = nicknameIdent[:pos]
    return (nickname, ident, hostname)
