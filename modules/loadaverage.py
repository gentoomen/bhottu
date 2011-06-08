from api import *

def load():
    """Shows the system load."""
    registerFunction("load average", loadAverage)
registerModule('LoadAverage', load)

def loadAverage(channel):
    """Shows the system load."""
    try:
        with open("/proc/loadavg") as file:
            average = file.read()
    except:
        sendMessage(channel, "Load data not available.")
        return
    sendMessage(channel, average)
