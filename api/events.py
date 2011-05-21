import stringmatcher
import authorize
import irc
import ircstatus
import log
import traceback

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
# A function can furthermore be marked as `implicit`, meaning that it will trigger
#   even when the message is not prefixed with 'bhottu, ';
# it can be `restricted`, which means that only authorized users can trigger it;
# and `errorMessages` can be set (which is the default), which means that an error
#   message will be sent when the syntax is wrong or the user is not authorized.
#

_functionHandlers = []

def registerFunction(format, function, syntax = None, module = None, implicit = False, restricted = False, errorMessages = True):
    global _functionHandlers
    parsedFormat = stringmatcher.parseFormat(format)
    (name, attemptFormat) = _functionName(parsedFormat)
    registration = Handler()
    registration.enabled = True
    registration.type = _functionHandlers
    registration.function = function
    registration.module = _effectiveModule(module)
    registration.format = parsedFormat
    registration.attemptFormat = attemptFormat
    registration.name = name
    registration.description = function.__doc__
    registration.syntax = syntax
    registration.syntaxErrorMessage = None
    registration.implicit = implicit
    registration.restricted = restricted
    registration.restrictedErrorMessage = None
    registration.errorMessages = errorMessages
    if registration.module != None:
        registration.module.handlers.append(registration)
    _functionHandlers.append(registration)
    return registration

def _functionName(format):
    outputString = ''
    outputFormat = []
    currentString = ''
    currentFormat = []
    if len(format) == 0 or format[0][0] != 'literal':
        raise ValueError, 'Invalid function format'
    for (type, argument) in format:
        if type == 'literal':
            currentString += argument
            currentFormat.append((type, argument))
        elif type == 'space':
            outputString += currentString
            outputFormat.extend(currentFormat)
            currentString = ' '
            currentFormat = [(type, argument)]
        else:
            break
    else:
        outputString += currentString
        outputFormat.extend(currentFormat)
    outputFormat.append(('space', None))
    outputFormat.append(('specifier', '!S'))
    return (outputString, outputFormat)

def functionList():
    global _functionHandlers
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

def registerMessageHandler(format, function, module = None, implicit = False):
    global _messageHandlers
    if format == None:
        parsedFormat = None
    else:
        parsedFormat = stringmatcher.parseFormat(format)
    registration = Handler()
    registration.enabled = True
    registration.type = _functionHandlers
    registration.function = function
    registration.module = _effectiveModule(module)
    registration.format = parsedFormat
    registration.implicit = implicit
    if registration.module != None:
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
        registration.enabled = False
        return True
    global _functionHandlers
    if registration.type == _functionHandlers:
        _functionHandlers.remove(registration)
        registration.enabled = False
        return True
    global _messageHandlers
    if registration.type == _messageHandlers:
        _messageHandlers.remove(registration)
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
    if message.startswith(ircstatus.currentNickname()):
        reducedMessage = message[len(ircstatus.currentNickname()):]
        if reducedMessage[:2].rstrip(' \t') in [',', ':']:
            message = reducedMessage[2:]
            triggered = True
    authorized = authorize.isAuthorized(nickname)
    
    global _functionHandlers
    for handler in _functionHandlers[:]:
        if not handler.enabled:
            continue
        # If the incoming message does not start with 'bhottu, ', ignore it
        # unless this function is marked Implicit.
        if not handler.implicit and not triggered:
            continue
        if stringmatcher.matchFormat(message, handler.attemptFormat) == None:
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
        if handler.restricted and not authorized:
            if handler.errorMessages:
                if handler.restrictedErrorMessage != None:
                    irc.sendMessage(channel, handler.restrictedErrorMessage)
                else:
                    irc.sendMessage(channel, 'Sorry, authorized users only.')
            continue
        # Everything checks out, we can execute the function.
        callFunction(handler.function, [channel, nickname] + arguments)
    
    global _messageHandlers
    for handler in _messageHandlers[:]:
        if not handler.enabled:
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
        if arguments == True or arguments == False:
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
