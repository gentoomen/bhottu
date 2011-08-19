import re
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

def parseFormat(format):
    pattern = ""
    specifiers = []
    attemptPattern = None
    while format != '':
        if format[0] == ' ':
            i = 1
            while i < len(format) and format[i] == ' ':
                i += 1
            pattern += '(?:\\s*(?<=\\s)|$)'
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
            pattern += re.escape(format[:i].replace('%%', '%'))
            format = format[i:]
        else:
            optional = False
            index = 1
            if attemptPattern == None:
                attemptPattern = pattern
            if index >= len(format):
                raise ValueError, 'Invalid format string: unfinished specifier'
            if format[index] == '!':
                optional = True
                index += 1
                if index >= len(format):
                    raise ValueError, 'Invalid format string: unfinished specifier'
            if format[index] == 'i':
                pattern += '([-+]?[0-9]+)'
            elif format[index] == 'f':
                pattern += '((?:[-+]?[0-9]+.?[0-9]*)|(?:[-+]?[0-9]*.?[0-9]+))'
            elif format[index] == 's':
                pattern += '((?:[^\'\"\\s][\\S]*)|(?:\'(?:[^\'\\\\]|(?:\\\\.))*\')|(?:\"(?:[^\"\\\\]|(?:\\\\.))*\"))'
            elif format[index] == 'S':
                pattern += '(\\S(?:.+(?:\\S|$)))'
            else:
                raise ValueError, 'Invalid format string: unknown specifier'
            if optional:
                pattern += '?'
            specifiers.append(format[1:index+1])
            format = format[index + 1:]
    regex = re.compile(pattern + '$', re.IGNORECASE)
    if attemptPattern == None:
        attemptPattern = pattern
    if attemptPattern == "":
        attemptRegex = None
    else:
        attemptRegex = re.compile(attemptPattern, re.IGNORECASE)
    return (regex, specifiers, attemptRegex)

def matchFormat(string, format):
    (regex, specifiers, attemptRegex) = format
    match = regex.match(string)
    if match == None:
        return None
    output = []
    for i in range(len(specifiers)):
        item = match.group(i + 1)
        if item == None:
            output.append(None)
        elif specifiers[i][-1] == 'i':
            output.append(int(item))
        elif specifiers[i][-1] == 'f':
            output.append(float(item))
        elif specifiers[i][-1] == 'S':
            output.append(item)
        elif specifiers[i][-1] == 's':
            if item[0] == '"' or item[0] == "'":
                output.append(re.sub('\\\\(.)', '\\1', item[1:-1]))
            else:
                output.append(item)
        else:
            raise ValueError, 'Invalid format'
    return output

def matchAttempt(string, format):
    (regex, specifiers, attemptRegex) = format
    return attemptRegex.match(string) != None
