import stringmatcher
import irc
import log
import traceback
import threading
import time

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
    if module == None:
        return _loadingModule
    return module

class Service(threading.Thread):
    """
    Simple service, will run until it is aborted, or function returns None

    ## Minimal example:
    def serviceSetup(service):
        pass
    def serviceFunction(service, state):
        return state
    def serviceCleanup(service):
        pass
    registerService(serviceSetup, serviceFunction, serviceCleanup)
    """
    def __init__(self, setup, function, cleanup, state=True):
        super(Service, self).__init__()
        self.daemon = True
        self._cleanup = cleanup
        self._aborted = False
        self._function = function
        self._setup_finished = False
        self.state = state
        self.sleeptime = 1
        self.setup = setup

    def abort(self):
        self._aborted = True

    def run(self):
        if not self._setup_finished:
            self.setup(self)
            self._setup_finished = True

        while self.state != None and not self._aborted:
            time.sleep(self.sleeptime)
            self.state = self._function(self, self.state)
        self._cleanup(self.state)

def _registerService(setup, function, cleanup, module, type = "service"):
    service = Service(setup, function, cleanup)
    service.module = _effectiveModule(module)
    service.enabled = True
    service.type = type
    if service.module != None:
        service.module.services.append(service)
    return service

def registerService(setup, function, cleanup, module = None):
    service = _registerService(setup, function, cleanup, module)
    return service

def _registerHandler(function, module, list, type = None):
    if type == None:
        type = list
    registration = Handler()
    registration.enabled = True
    registration.type = type
    registration.function = function
    registration.module = _effectiveModule(module)
    if registration.module != None:
        registration.module.handlers.append(registration)
    list.append(registration)
    return registration

#
# An UnloadHandler gets called when its module gets unloaded.
#

def registerUnloadHandler(function, targetModule = None, callingModule = None):
    targetModule = _effectiveModule(targetModule)
    registration = _registerHandler(function, callingModule, targetModule.unloadHandlers, "UnloadHandler")
    registration.targetModule = targetModule
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
    if command not in _commandHandlers:
        _commandHandlers[command] = []
    registration = _registerHandler(function, module, _commandHandlers[command], _commandHandlers)
    registration.command = command
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
# A function can furthermore be marked as `implicit`, meaning that it will trigger
#   even when the message is not prefixed with 'bhottu, ';
# it can be `restricted`, which means that only authorized users can trigger it;
# and `errorMessages` can be set (which is the default), which means that an error
#   message will be sent when the syntax is wrong or the user is not authorized.
#

_functionHandlers = []

def registerFunction(format, function, syntax = None, module = None, implicit = False, restricted = False, errorMessages = True, noIgnore = False):
    parsedFormat = stringmatcher.parseFormat(format)
    registration = _registerHandler(function, module, _functionHandlers)
    registration.format = parsedFormat
    registration.description = function.__doc__
    registration.syntax = syntax
    registration.syntaxErrorMessage = None
    registration.implicit = implicit
    registration.restricted = restricted
    registration.restrictedErrorMessage = None
    registration.errorMessages = errorMessages
    registration.noIgnore = noIgnore
    return registration
#
# decorators, it's what all the cool kids are doing these days
# use @register(format, ...) before a function definition to register it
#
def register(format, syntax = None, module = None, implicit = False, restricted = False, errorMessages = True, noIgnore = False):
    def register_deco(function):
        registerFunction(format, function, syntax, module, implicit, restricted, errorMessages, noIgnore)
    return register_deco    

def functionList():
    return _functionHandlers

#
# A MessageHandler uses the same syntax as a Function, but need not start with
# a literal; it also doesn't automatically appear in the help system,
# generate syntax hints, and stuff like that.
#
# If format == None, this registers the handler for any incoming message,
#   and `implicit` is ignored.
#

_messageHandlers = []

def registerMessageHandler(format, function, module = None, implicit = False, noIgnore = False):
    if format == None:
        parsedFormat = None
    else:
        parsedFormat = stringmatcher.parseFormat(format)
    registration = _registerHandler(function, module, _messageHandlers)
    registration.format = parsedFormat
    registration.implicit = implicit
    registration.noIgnore = noIgnore
    return registration

#
# Unregisters an UnloadHandler, ParsedCommandHandler, EventHandler, FunctionHandler, or MessageHandler.
#

def unregister(registration):
    for type in (_functionHandlers, _messageHandlers):
        if registration.type == type:
            type.remove(registration)
            registration.module.handlers.remove(registration)
            registration.enabled = False
            return True
    if registration.type == _commandHandlers:
        _commandHandlers[registration.command].remove(registration)
        registration.module.handlers.remove(registration)
        registration.enabled = False
        return True
    if registration.type == "UnloadHandler":
        registration.targetModule.unloadHandlers.remove(registration)
        registration.module.handlers.remove(registration)
        registration.enabled = False
        return True
    if registration.type == "service":
        registration.module.services.remove(registration)
        registration.abort()
        registration.enabled = False
    return False

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
    try:
        function(*arguments[:function.func_code.co_argcount])
    except Exception, description:
        log.warning("Function '%s' raised an exception: '%s'\n%s" % (function.__name__, description, traceback.format_exc()))

#
# moduleUnloadEvent is responsible for calling appropriate handlers for a module unload.
#

def moduleUnloadEvent(module):
    for handler in module.unloadHandlers[:]:
        if not handler.enabled:
            continue
        callFunction(handler.function, [])

import authorize
import ignorelist
import ircstatus


#
# incomingIrcEvent is responsible for acting on incoming irc events
# by parsing them and calling the appropriate handlers.
#

def incomingIrcEvent(event):
    (sender, command, arguments) = parseEvent(event)

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
        incomingIrcMessage(sender, arguments[0], arguments[1])

def incomingIrcMessage(sender, channel, fullMessage):
    # sender is a nickname!ident@hostname triple.
    (nickname, ident, hostname) = parseSender(sender)
    if channel.startswith('#') or channel.startswith('&'):
        triggered = False
    else:
        channel = nickname
        triggered = True
    message = fullMessage.lstrip(' \t')
    if message.lower().startswith(ircstatus.currentNickname().lower()):
        reducedMessage = message[len(ircstatus.currentNickname()):]
        if reducedMessage[:2].rstrip(' \t') in [',', ':']:
            message = reducedMessage[2:]
            triggered = True
    ignored = ignorelist.isIgnored(nickname)
    authorized = authorize.isAuthorized(nickname)
    
    for handler in _functionHandlers[:]:
        if not handler.enabled:
            continue
        # If the person in question is ignored, disregard the command.
        if ignored and not handler.noIgnore:
            continue
        # If the incoming message does not start with 'bhottu, ', ignore it
        # unless this function is marked Implicit.
        if not handler.implicit and not triggered:
            continue
        if not stringmatcher.matchAttempt(message, handler.format):
            # The function was not called.
            continue
        arguments = stringmatcher.matchFormat(message, handler.format)
        if arguments == None:
            # The function matches, but with wrong syntax.
            if handler.errorMessages:
                if handler.syntaxErrorMessage != None:
                    irc.sendMessage(channel, handler.syntaxErrorMessage)
                elif handler.syntax != None:
                    irc.sendMessage(channel, "syntax: %s" % handler.syntax)
            continue
        # If we get here, the function was matched.
        # If the user is not authorized to invoke this function, abort.

        # If the function is restricted, pass it to authorize.py, who will verify the user and execute it later
        if handler.restricted:
            if authorized:
                authorize.doIfAuthenticated(handler.function, channel, nickname, arguments)
            else:
                if handler.errorMessages:
                    if handler.restrictedErrorMessage != None:
                        irc.sendMessage(channel, handler.restrictedErrorMessage)
                    else:
                        irc.sendMessage(channel, "%s, %s03>implying" % (nickname, chr(3)))
            continue

        # Everything checks out, we can execute the function.
        callFunction(handler.function, [channel, nickname] + arguments)
    
    for handler in _messageHandlers[:]:
        if not handler.enabled:
            continue
        if ignored and not handler.noIgnore:
            continue
        # Handlers with format == None are a special case - they always get called, period.
        if handler.format == None:
            callFunction(handler.function, [channel, nickname, fullMessage])
            continue
        
        # If the incoming message does not start with 'bhottu, ', ignore it
        # unless this function is marked Implicit.
        if not handler.implicit and not triggered:
            continue
        arguments = stringmatcher.matchFormat(message, handler.format)
        if arguments == None:
            # No match.
            continue
        # We have a match, so execute the handler.
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
