import time
import traceback

_logfiles = []
_levels = {
    'PANIC' : 0,
    'ALERT' : 1,
    'CRITICAL' : 2,
    'ERROR' : 3,
    'WARNING' : 4,
    'NOTICE' : 5,
    'INFO' : 6,
    'DEBUG' : 7,
}

def addLog(file, level, verbose = False):
    global _levels
    global _logfiles
    if level == None:
        return True
    if level not in _levels:
        return False
    if isinstance(file, str):
        file = open(file, 'a')
    _logfiles.append((file, level, verbose))
    return True

def getCallingFunction(levels):
    trace = traceback.extract_stack()
    if len(trace) > levels:
        frame = trace[-levels - 1]
    else:
        frame = trace[0]
    return frame[2]

def doLog(loglevel, message):
    global _levels
    global _logfiles
    currentTime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    function = getCallingFunction(3) # 0 is getCallingFunction, 1 is doLog, 2 is panic/alert/debug/..., 3 is the real caller
    lightMessage = "[%s] %8s: %s\n" % (currentTime, loglevel, message)
    verboseMessage = "[%s] %8s: %20s(): %s\n" % (currentTime, loglevel, function, message)
    for (file, level, verbose) in _logfiles:
        if _levels[loglevel] <= _levels[level]:
            if verbose:
                file.write(verboseMessage)
            else:
                file.write(lightMessage)
            file.flush()

def panic(message):
    doLog('PANIC', message)

def alert(message):
    doLog('ALERT', message)

def critical(message):
    doLog('CRITICAL', message)

def error(message):
    doLog('ERROR', message)

def warning(message):
    doLog('WARNING', message)

def notice(message):
    doLog('NOTICE', message)

def info(message):
    doLog('INFO', message)

def debug(message):
    doLog('DEBUG', message)
