#
# Accepted format specifiers:
# %s - String terminated by the character directly following the %s.
# %S - String terminated by the end of the message. Must be at the very end of a format string.
# %i - Integer.
# %f - Floating point number.
# %% - Literal % character.
#
# Modifiers:
# ! - Marks the specifier as optional.
#
# Matching is greedy, so don't use optional specifiers at places other than the
# end of the string or in combination with %S unless you know what you're doing.
#

#
# A parsed format string is a list of match blocks.
# A match block is a pair (type, argument), where type is:
#   - 'literal': a literal string (stored as `argument`) should be matched.
#   - 'space': any nonempty amount of whitespace should be matched. `argument` is None.
#   - 'specifier': a format specifier (stored as `argument` without the %) should be matched.
# Example: parseFormat('chance %i%% %S') =
#    [ ('literal', 'chance'), ('space', None), ('specifier', 'i'), ('literal', '%'), ('space', None), ('specifier', 'S') ]
#

def parseFormat(format):
    output = []
    while format != '':
        if format[0] == ' ':
            i = 1
            while i < len(format) and format[i] == ' ':
                i += 1
            output.append(('space', None))
            format = format[i:]
        elif format[0] != '%' or (len(format) >= 2 and format[1] == '%'):
            i = 0
            while i < len(format):
                if format[i] != ' ' and format[i] != '%':
                    i += 1
                    continue
                if format[i : i + 2] == '%%':
                    i += 2
                    continue
                break
            output.append(('literal', format[:i].replace('%%', '%')))
            format = format[i:]
        else:
            index = 1
            if index >= len(format):
                raise ValueError, 'Invalid format string: unfinished specifier'
            if format[index] == '!':
                index += 1
                if index >= len(format):
                    raise ValueError, 'Invalid format string: unfinished specifier'
            if format[index] not in ['s', 'S', 'i', 'f']:
                raise ValueError, 'Invalid format string: unknown specifier'
            if len(output) > 0 and output[-1][0] == 'specifier':
                raise ValueError, 'Invalid format string: two specifiers must be separated by some literal or whitespace'
            output.append(('specifier', format[1:index + 1]))
            format = format[index + 1:]
    return output

#
# Matches a string against a parsed format string.
# Returns a list of matched arguments on success;
# if the match fails, returns either True if at least one literal was matched,
# or False it none was.
#

def matchFormat(string, format):
    output = []
    literalMatched = False
    lastSeen = None
    for (type, argument) in format:
        if type == 'literal':
            if string.startswith(argument):
                string = string[len(argument):]
                literalMatched = True
                lastSeen = 'literal'
            else:
                return literalMatched
        elif type == 'space':
            reducedString = string.lstrip(' \t')
            # Space blocks are idenpotent, that is, matching two adjacent space
            # blocks is equivalent to matching a single space block. This includes
            # two space blocks with an absent optional parameter in between.
            if string != reducedString or len(string) == 0 or lastSeen == 'space':
                string = reducedString
                lastSeen = 'space'
            else:
                return literalMatched
        elif type == 'specifier':
            optional = argument[0] == '!'
            parameter = argument[-1]
            
            if parameter == 'i':
                (argValue, argString) = matchInteger(string)
            elif parameter == 'f':
                (argValue, argString) = matchFloat(string)
            elif parameter == 's':
                (argValue, argString) = matchString(string)
            elif parameter == 'S':
                (argValue, argString) = (string, string)
            else:
                raise ValueError, 'Unknown format specifier "%s"' % argument
            
            if argValue == None:
                if optional:
                    output.append(argValue)
                else:
                    return literalMatched
            else:
                output.append(argValue)
                string = string[len(argString):]
                lastSeen = 'specifier'
        else:
            raise ValueError, 'Unknown format block "%s"' % type
    return output

def matchInteger(string):
    digitMatched = False
    index = 0
    if index < len(string) and (string[index] == '+' or string[index] == '-'):
        index += 1
    while index < len(string) and string[index].isdigit():
        index += 1
        digitMatched = True
    if not digitMatched:
        return (None, None)
    output = string[:index]
    try:
        return (int(output), output)
    except Exception:
        return (None, None)

def matchFloat(string):
    digitMatched = False
    index = 0
    if index < len(string) and (string[index] == '+' or string[index] == '-'):
        index += 1
    while index < len(string) and string[index].isdigit():
        index += 1
        digitMatched = True
    if index < len(string) and string[index] == '.':
        index += 1
    while index < len(string) and string[index].isdigit():
        index += 1
        digitMatched = True
    if not digitMatched:
        return (None, None)
    output = string[:index]
    try:
        return (float(output), output)
    except Exception:
        return (None, None)

def matchString(string):
    if string == '':
        return (None, None)
    elif string[0] == "'":
        output = ''
        index = 1
        while index < len(string):
            if string[index] == "'":
                index += 1
                return (output, string[:index])
            elif string[index] != '\\':
                output += string[index]
                index += 1
            else:
                index += 1
                if not index < len(string):
                    break
                output += string[index]
                index += 1
        return (None, None)
    elif string[0] == '"':
        output = ''
        index = 1
        while index < len(string):
            if string[index] == '"':
                index += 1
                return (output, string[:index])
            elif string[index] != '\\':
                output += string[index]
                index += 1
            else:
                index += 1
                if not index < len(string):
                    break
                output += string[index]
                index += 1
        return (None, None)
    else:
        index = 0
        while index < len(string) and string[index] != ' ' and string[index] != '\t':
            index += 1
        output = string[:index]
        return (output, output)
