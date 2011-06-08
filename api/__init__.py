import log
from database import *
from irc import *
from ircstatus import *
from events import *
from modules import *
from authorize import *
from ignorelist import *

#
# HACK ALERT:
# There is a circular dependency between ircstatus and events
# (ircstatus registers events to main status, events needs to
# know the currentNick status to determine when the bot is
# begin addressed), which is resolved by loading ircstatus
# *before* events. Therefore, the above import order is important.
#
